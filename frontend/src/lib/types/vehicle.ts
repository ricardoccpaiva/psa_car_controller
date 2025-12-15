export interface Vehicle {
	vin: string;
	vehicle_id: string;
	label: string;
	brand: string;
	battery_power?: number;
	fuel_capacity?: number;
	max_elec_consumption?: number;
	max_fuel_consumption?: number;
	status?: VehicleStatus;
}

export interface VehicleStatus {
	energy?: Energy[];
	last_position?: Position;
	timed_odometer?: {
		mileage: number;
	};
	preconditionning?: {
		air_conditioning?: {
			status: string;
		};
	};
}

export interface Energy {
	type: string;
	level: number;
	charging?: {
		status: string;
		plugged: boolean;
	};
	updated_at?: string;
}

export interface Position {
	type: string;
	geometry: {
		type: string;
		coordinates: [number, number, number?]; // [longitude, latitude, altitude?]
	};
	properties?: {
		updated_at: string;
	};
}

export interface Trip {
	id: number;
	start_at: string;
	end_at: string;
	duration: number;
	distance: number;
	mileage: number;
	speed_average: number;
	consumption_km?: number;
	consumption_fuel_km?: number;
	altitude_diff?: number;
	start_level?: number;
	end_level?: number;
}

export interface Charge {
	start_at: string;
	stop_at: string;
	start_level: number;
	end_level: number;
	co2: number;
	kw: number;
	price: number;
	charging_mode: string;
	mileage: number;
	duration?: number;
}
