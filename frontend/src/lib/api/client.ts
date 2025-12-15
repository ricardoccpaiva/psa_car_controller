/**
 * API Client for PSA Car Controller Backend
 * Handles all HTTP requests to the Flask REST API
 */

// API base URL - can be configured via environment variables
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export class ApiError extends Error {
	constructor(
		message: string,
		public status: number,
		public response?: any
	) {
		super(message);
		this.name = 'ApiError';
	}
}

/**
 * Generic API request function
 */
export async function apiRequest<T>(
	endpoint: string,
	options?: RequestInit
): Promise<T> {
	const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;

	try {
		const response = await fetch(url, {
			...options,
			headers: {
				'Content-Type': 'application/json',
				...options?.headers
			}
		});

		if (!response.ok) {
			let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
			let errorData;

			try {
				errorData = await response.json();
				errorMessage = errorData.error || errorData.message || errorMessage;
			} catch {
				// Response is not JSON, use status text
			}

			throw new ApiError(errorMessage, response.status, errorData);
		}

		// Handle empty responses
		const text = await response.text();
		if (!text) {
			return null as T;
		}

		return JSON.parse(text) as T;
	} catch (error) {
		if (error instanceof ApiError) {
			throw error;
		}

		// Network or parsing error
		throw new ApiError(
			error instanceof Error ? error.message : 'Network request failed',
			0
		);
	}
}

/**
 * GET request
 */
export async function get<T>(endpoint: string): Promise<T> {
	return apiRequest<T>(endpoint, { method: 'GET' });
}

/**
 * POST request
 */
export async function post<T>(endpoint: string, data?: any): Promise<T> {
	return apiRequest<T>(endpoint, {
		method: 'POST',
		body: data ? JSON.stringify(data) : undefined
	});
}

/**
 * PUT request
 */
export async function put<T>(endpoint: string, data?: any): Promise<T> {
	return apiRequest<T>(endpoint, {
		method: 'PUT',
		body: data ? JSON.stringify(data) : undefined
	});
}

/**
 * PATCH request
 */
export async function patch<T>(endpoint: string, data?: any): Promise<T> {
	return apiRequest<T>(endpoint, {
		method: 'PATCH',
		body: data ? JSON.stringify(data) : undefined
	});
}

/**
 * DELETE request
 */
export async function del<T>(endpoint: string): Promise<T> {
	return apiRequest<T>(endpoint, { method: 'DELETE' });
}
