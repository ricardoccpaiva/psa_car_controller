/**
 * TanStack Query hooks for data fetching
 */
import { createQuery, createMutation, useQueryClient } from '@tanstack/svelte-query';
import { get, post } from './client';
import type { Vehicle, Trip, Charge } from '$lib/types/vehicle';

/**
 * Fetch all vehicles
 */
export function createVehiclesQuery() {
	return createQuery({
		queryKey: ['vehicles'],
		queryFn: () => get<Vehicle[]>('/get_vehicles')
	});
}

/**
 * Fetch vehicle info by VIN
 */
export function createVehicleInfoQuery(vin: string, fromCache: boolean = false) {
	return createQuery({
		queryKey: ['vehicle', vin, fromCache],
		queryFn: () => get<Vehicle>(`/get_vehicleinfo/${vin}?from_cache=${fromCache ? 1 : 0}`),
		enabled: !!vin
	});
}

/**
 * Fetch all trips
 */
export function createTripsQuery() {
	return createQuery({
		queryKey: ['trips'],
		queryFn: () => get<Trip[]>('/vehicles/trips')
	});
}

/**
 * Fetch all charging sessions
 */
export function createChargingsQuery() {
	return createQuery({
		queryKey: ['chargings'],
		queryFn: () => get<Charge[]>('/vehicles/chargings')
	});
}

/**
 * Fetch recorded positions (GeoJSON)
 */
export function createPositionsQuery() {
	return createQuery({
		queryKey: ['positions'],
		queryFn: () => get<any>('/positions')
	});
}

/**
 * Fetch settings
 */
export function createSettingsQuery() {
	return createQuery({
		queryKey: ['settings'],
		queryFn: () => get<any>('/settings')
	});
}

/**
 * Fetch battery state of health
 */
export function createBatterySOHQuery(vin: string) {
	return createQuery({
		queryKey: ['battery-soh', vin],
		queryFn: () => get<{ soh: number }>(`/battery/soh/${vin}`),
		enabled: !!vin
	});
}

/**
 * Mutation: Charge Now
 */
export function createChargeNowMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: ({ vin, charge }: { vin: string; charge: boolean }) =>
			get(`/charge_now/${vin}/${charge ? 1 : 0}`),
		onSuccess: (_, variables) => {
			// Invalidate vehicle info to refresh status
			queryClient.invalidateQueries({ queryKey: ['vehicle', variables.vin] });
		}
	});
}

/**
 * Mutation: Wakeup Vehicle
 */
export function createWakeupMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: (vin: string) => get(`/wakeup/${vin}`),
		onSuccess: (_, vin) => {
			queryClient.invalidateQueries({ queryKey: ['vehicle', vin] });
		}
	});
}

/**
 * Mutation: Preconditioning
 */
export function createPreconditioningMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: ({ vin, activate }: { vin: string; activate: boolean }) =>
			get(`/preconditioning/${vin}/${activate ? 1 : 0}`),
		onSuccess: (_, variables) => {
			queryClient.invalidateQueries({ queryKey: ['vehicle', variables.vin] });
		}
	});
}

/**
 * Mutation: Sound Horn
 */
export function createHornMutation() {
	return createMutation({
		mutationFn: ({ vin, count }: { vin: string; count: number }) => get(`/horn/${vin}/${count}`)
	});
}

/**
 * Mutation: Flash Lights
 */
export function createLightsMutation() {
	return createMutation({
		mutationFn: ({ vin, duration }: { vin: string; duration: number }) =>
			get(`/lights/${vin}/${duration}`)
	});
}

/**
 * Mutation: Lock/Unlock Doors
 */
export function createLockDoorMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: ({ vin, lock }: { vin: string; lock: boolean }) =>
			get(`/lock_door/${vin}/${lock ? 1 : 0}`),
		onSuccess: (_, variables) => {
			queryClient.invalidateQueries({ queryKey: ['vehicle', variables.vin] });
		}
	});
}
