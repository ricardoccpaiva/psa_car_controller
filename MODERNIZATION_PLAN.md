# PSA Car Controller - Frontend Modernization Plan

## 🎯 Objective
Migrate from Python Dash framework to a modern SvelteKit frontend while preserving all existing functionality.

---

## 📋 Tech Stack

### Frontend (New)
- **Framework**: SvelteKit (SSR + SPA capabilities)
- **Language**: TypeScript
- **UI Components**: shadcn-svelte (Tailwind-based)
- **Styling**: Tailwind CSS
- **Charts**: Chart.js + svelte-chartjs
- **Maps**: Mapbox GL JS
- **State Management**:
  - Svelte stores (global state)
  - TanStack Query (@tanstack/svelte-query) for server state
- **Tables**: TanStack Table (@tanstack/svelte-table)
- **Forms**: Superforms + Zod validation
- **HTTP Client**: Fetch API with TanStack Query

### Backend (Existing - Enhanced)
- **Framework**: Flask (keep as REST API)
- **Add**: Flask-CORS for proper CORS handling
- **Add**: Better error responses (JSON format)
- **Keep**: All existing PSA API integration, database, business logic

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   SvelteKit Frontend                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Routes     │  │  Components  │  │    Stores    │ │
│  │ (pages)      │  │ (shadcn-ui)  │  │  (state)     │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                  │                  │         │
│         └──────────────────┴──────────────────┘         │
│                           │                             │
│                  ┌────────▼────────┐                    │
│                  │ TanStack Query  │                    │
│                  │ (data fetching) │                    │
│                  └────────┬────────┘                    │
└───────────────────────────┼─────────────────────────────┘
                            │
                   ┌────────▼────────┐
                   │   REST API      │
                   │  (Fetch/JSON)   │
                   └────────┬────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│                    Flask Backend                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  API Routes  │  │  PSA Client  │  │   Database   │ │
│  │  (REST)      │  │  (OAuth)     │  │   (SQLite)   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 New Project Structure

```
psa_car_controller/
├── frontend/                      # NEW: SvelteKit app
│   ├── src/
│   │   ├── routes/
│   │   │   ├── +layout.svelte          # Root layout with nav
│   │   │   ├── +page.svelte            # Dashboard (home)
│   │   │   ├── trips/
│   │   │   │   └── +page.svelte        # Trips page
│   │   │   ├── charging/
│   │   │   │   └── +page.svelte        # Charging page
│   │   │   ├── map/
│   │   │   │   └── +page.svelte        # Map page
│   │   │   ├── control/
│   │   │   │   └── +page.svelte        # Vehicle control
│   │   │   ├── config/
│   │   │   │   ├── +page.svelte        # Config hub
│   │   │   │   ├── login/
│   │   │   │   │   └── +page.svelte    # OAuth setup
│   │   │   │   ├── otp/
│   │   │   │   │   └── +page.svelte    # OTP verification
│   │   │   │   └── oauth/
│   │   │   │       └── +page.svelte    # OAuth callback
│   │   │   └── log/
│   │   │       └── +page.svelte        # Log viewer
│   │   ├── lib/
│   │   │   ├── components/
│   │   │   │   ├── ui/                 # shadcn-svelte components
│   │   │   │   │   ├── button.svelte
│   │   │   │   │   ├── card.svelte
│   │   │   │   │   ├── table.svelte
│   │   │   │   │   ├── input.svelte
│   │   │   │   │   ├── select.svelte
│   │   │   │   │   ├── tabs.svelte
│   │   │   │   │   ├── modal.svelte
│   │   │   │   │   ├── alert.svelte
│   │   │   │   │   └── ...
│   │   │   │   ├── charts/
│   │   │   │   │   ├── ConsumptionChart.svelte
│   │   │   │   │   ├── BatteryCurveChart.svelte
│   │   │   │   │   ├── AltitudeChart.svelte
│   │   │   │   │   └── MapChart.svelte
│   │   │   │   ├── tables/
│   │   │   │   │   ├── TripsTable.svelte
│   │   │   │   │   └── ChargingTable.svelte
│   │   │   │   ├── cards/
│   │   │   │   │   └── SummaryCard.svelte
│   │   │   │   └── controls/
│   │   │   │       ├── VehicleControl.svelte
│   │   │   │       ├── ChargeControl.svelte
│   │   │   │       └── PreconditionControl.svelte
│   │   │   ├── stores/
│   │   │   │   ├── auth.ts             # Auth state
│   │   │   │   ├── vehicles.ts         # Vehicle data
│   │   │   │   └── filters.ts          # Date range filters
│   │   │   ├── api/
│   │   │   │   ├── client.ts           # Base API client
│   │   │   │   ├── queries.ts          # TanStack Query hooks
│   │   │   │   └── mutations.ts        # TanStack mutations
│   │   │   ├── types/
│   │   │   │   ├── vehicle.ts
│   │   │   │   ├── trip.ts
│   │   │   │   ├── charge.ts
│   │   │   │   └── api.ts
│   │   │   └── utils/
│   │   │       ├── date.ts
│   │   │       ├── format.ts
│   │   │       └── calculations.ts
│   │   └── app.html
│   ├── static/
│   │   └── images/                     # SVG icons, logos
│   ├── package.json
│   ├── tsconfig.json
│   ├── svelte.config.js
│   ├── tailwind.config.js
│   └── vite.config.ts
│
├── psa_car_controller/                # EXISTING: Python backend
│   ├── web/
│   │   ├── api.py                     # MODIFIED: Pure REST API routes
│   │   ├── app.py                     # MODIFIED: Remove Dash, serve SvelteKit build
│   │   └── ...                        # Keep existing business logic
│   └── ...
└── MODERNIZATION_PLAN.md             # This file
```

---

## 🔄 Migration Phases

### Phase 1: Project Setup ✅
**Duration**: ~2 hours

1. **Initialize SvelteKit Project**
   ```bash
   cd psa_car_controller
   npm create svelte@latest frontend
   # Choose: Skeleton project, TypeScript, ESLint, Prettier
   cd frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install -D tailwindcss postcss autoprefixer
   npx tailwindcss init -p

   npm install -D @tailwindcss/typography @tailwindcss/forms

   npx shadcn-svelte@latest init
   # Follow prompts for shadcn-svelte setup

   npm install @tanstack/svelte-query
   npm install @tanstack/svelte-table
   npm install chart.js svelte-chartjs
   npm install mapbox-gl
   npm install date-fns
   npm install superforms zod
   ```

3. **Configure Tailwind**
   - Set up `tailwind.config.js` with shadcn theme
   - Add Tailwind directives to `app.css`

4. **Configure TypeScript**
   - Strict mode enabled
   - Path aliases (`$lib/*`)

---

### Phase 2: Backend API Refactor ✅
**Duration**: ~4 hours

1. **Convert Flask to Pure REST API**
   - Remove all Dash-specific code from `web/app.py`
   - Keep Flask app for API routes only
   - Add Flask-CORS for cross-origin requests

   ```python
   # web/api.py - Example refactor
   from flask import Flask, jsonify, request
   from flask_cors import CORS

   app = Flask(__name__)
   CORS(app)  # Enable CORS for SvelteKit dev server

   @app.route('/api/vehicles', methods=['GET'])
   def get_vehicles():
       try:
           vehicles = VEHICLE_SERVICE.get_vehicles()
           return jsonify([v.to_dict() for v in vehicles])
       except Exception as e:
           return jsonify({"error": str(e)}), 500
   ```

2. **Standardize API Responses**
   - All endpoints return JSON
   - Consistent error format: `{"error": "message", "code": 400}`
   - Success format: `{"data": {...}, "message": "optional"}`

3. **Update All Routes to `/api/*`**
   ```
   /get_vehicles          → /api/vehicles
   /get_vehicleinfo/<vin> → /api/vehicles/<vin>
   /vehicles/trips        → /api/trips
   /vehicles/chargings    → /api/chargings
   /charge_now/<vin>      → /api/vehicles/<vin>/charge (POST)
   /wakeup/<vin>          → /api/vehicles/<vin>/wakeup (POST)
   etc.
   ```

4. **Test API Endpoints**
   - Use Postman/Insomnia to verify all endpoints
   - Document API with examples

---

### Phase 3: Core Layout & Navigation ✅
**Duration**: ~3 hours

1. **Create Root Layout** (`src/routes/+layout.svelte`)
   - Header with navigation
   - Footer (optional)
   - TanStack Query provider setup

2. **Install shadcn Components**
   ```bash
   npx shadcn-svelte@latest add button
   npx shadcn-svelte@latest add card
   npx shadcn-svelte@latest add tabs
   npx shadcn-svelte@latest add input
   npx shadcn-svelte@latest add select
   npx shadcn-svelte@latest add table
   npx shadcn-svelte@latest add dialog
   npx shadcn-svelte@latest add alert
   npx shadcn-svelte@latest add badge
   npx shadcn-svelte@latest add slider
   ```

3. **Build Navigation Component**
   - Logo/title
   - Main nav links (Dashboard, Trips, Charging, Map, Control, Config)
   - Settings icon
   - Version badge (link to GitHub releases)
   - Responsive mobile menu

4. **Create Theme System**
   - Light/dark mode toggle (optional enhancement)
   - CSS variables for consistent colors

---

### Phase 4: Authentication & State Management ✅
**Duration**: ~5 hours

1. **Create Auth Store** (`src/lib/stores/auth.ts`)
   ```typescript
   import { writable } from 'svelte/store';

   interface AuthState {
     isAuthenticated: boolean;
     isGood: boolean;  // Matches APP.is_good
   }

   export const authStore = writable<AuthState>({
     isAuthenticated: false,
     isGood: false
   });
   ```

2. **Set Up TanStack Query**
   ```typescript
   // src/routes/+layout.svelte
   import { QueryClient, QueryClientProvider } from '@tanstack/svelte-query';

   const queryClient = new QueryClient({
     defaultOptions: {
       queries: {
         staleTime: 60_000, // 1 minute
         retry: 1
       }
     }
   });
   ```

3. **Create API Client** (`src/lib/api/client.ts`)
   ```typescript
   const API_BASE = 'http://localhost:5000/api';

   export async function apiRequest<T>(
     endpoint: string,
     options?: RequestInit
   ): Promise<T> {
     const response = await fetch(`${API_BASE}${endpoint}`, {
       ...options,
       headers: {
         'Content-Type': 'application/json',
         ...options?.headers
       }
     });

     if (!response.ok) {
       const error = await response.json();
       throw new Error(error.message || 'API request failed');
     }

     return response.json();
   }
   ```

4. **Implement OAuth Flow Pages**
   - `/config/login` - Initial setup form
   - `/config/otp` - OTP verification
   - `/config/oauth` - OAuth callback handler

---

### Phase 5: Dashboard Page ✅
**Duration**: ~4 hours

1. **Create Summary Cards Component**
   ```svelte
   <!-- src/lib/components/cards/SummaryCard.svelte -->
   <script lang="ts">
     export let title: string;
     export let value: string;
     export let unit: string;
     export let icon: string;
   </script>

   <Card>
     <CardHeader>
       <img src={icon} alt={title} class="w-6 h-6" />
       <CardTitle>{title}</CardTitle>
     </CardHeader>
     <CardContent>
       <div class="text-3xl font-bold">{value}</div>
       <p class="text-sm text-muted-foreground">{unit}</p>
     </CardContent>
   </Card>
   ```

2. **Build Dashboard Layout**
   - Grid of 4 summary cards
   - Quick stats (avg consumption, emissions, charge speed, costs)
   - Responsive grid (1 col mobile, 2 cols tablet, 4 cols desktop)

3. **Fetch Data with TanStack Query**
   ```typescript
   // src/lib/api/queries.ts
   import { createQuery } from '@tanstack/svelte-query';
   import { apiRequest } from './client';

   export function createTripsQuery() {
     return createQuery({
       queryKey: ['trips'],
       queryFn: () => apiRequest<Trip[]>('/trips')
     });
   }
   ```

4. **Calculate Summary Stats**
   - Reuse calculation logic from `clientside.js`
   - Create utility functions in `src/lib/utils/calculations.ts`

---

### Phase 6: Trips Page ✅
**Duration**: ~6 hours

1. **Create Trips Table Component**
   - Use TanStack Table for sorting, pagination
   - Columns: ID, Start At, Duration, Avg Speed, Consumption, Distance, Mileage, Altitude Diff
   - Export to CSV/Excel functionality
   - Row click → show altitude modal

2. **Build Chart Components**
   - `ConsumptionTimelineChart.svelte` - Histogram by date
   - `ConsumptionBySpeedChart.svelte` - Scatter plot
   - `ConsumptionByTempChart.svelte` - Temperature correlation

   Example with Chart.js:
   ```svelte
   <script lang="ts">
     import { Bar } from 'svelte-chartjs';
     import { Chart, registerables } from 'chart.js';

     Chart.register(...registerables);

     export let trips: Trip[];

     $: chartData = {
       labels: trips.map(t => formatDate(t.start_at)),
       datasets: [{
         label: 'Consumption',
         data: trips.map(t => t.consumption_km)
       }]
     };
   </script>

   <Bar data={chartData} />
   ```

3. **Add Date Range Filter**
   - Slider component (or date picker)
   - Filter trips by date range
   - Update charts and table reactively

4. **Altitude Modal**
   - Dialog component
   - Line chart showing altitude changes
   - Open on table row altitude_diff click

---

### Phase 7: Charging Page ✅
**Duration**: ~6 hours

1. **Create Charging Table Component**
   - Editable price column
   - Color coding (low battery = red, high charge = green, quick charge = yellow bg)
   - Export functionality
   - Row click on start/end level → battery curve modal

2. **Implement Inline Editing**
   ```svelte
   <script lang="ts">
     import { createMutation } from '@tanstack/svelte-query';

     const updatePrice = createMutation({
       mutationFn: (params: {id: number, price: number}) =>
         apiRequest(`/chargings/${params.id}`, {
           method: 'PATCH',
           body: JSON.stringify({ price: params.price })
         }),
       onSuccess: () => {
         // Refetch table data
       }
     });

     function handlePriceChange(id: number, newPrice: number) {
       $updatePrice.mutate({ id, price: newPrice });
     }
   </script>
   ```

3. **Battery Curve Chart**
   - Modal with line chart
   - X-axis: Battery percentage
   - Y-axis: Charging speed (kW)
   - Show efficiency curve

4. **Charging Summary Cards**
   - Average charge speed
   - Total electricity cost
   - CO2 emissions

---

### Phase 8: Map Page ✅
**Duration**: ~4 hours

1. **Integrate Mapbox GL**
   ```svelte
   <script lang="ts">
     import mapboxgl from 'mapbox-gl';
     import { onMount } from 'svelte';

     let mapContainer: HTMLDivElement;
     let map: mapboxgl.Map;

     onMount(() => {
       mapboxgl.accessToken = 'YOUR_TOKEN';

       map = new mapboxgl.Map({
         container: mapContainer,
         style: 'mapbox://styles/mapbox/streets-v12',
         center: [0, 0],
         zoom: 2
       });

       // Add trip paths
       map.on('load', () => {
         map.addSource('trips', {
           type: 'geojson',
           data: tripsGeoJSON
         });

         map.addLayer({
           id: 'trips',
           type: 'line',
           source: 'trips',
           paint: {
             'line-color': '#3887be',
             'line-width': 3
           }
         });
       });
     });
   </script>

   <div bind:this={mapContainer} class="w-full h-[600px]" />
   ```

2. **Display Trip Paths**
   - Fetch positions from `/api/positions`
   - Convert to GeoJSON format
   - Render as line layer

3. **Add Last Position Marker**
   - Custom marker with vehicle icon
   - Popup with current battery level, mileage

4. **Filter by Date Range**
   - Same slider as trips/charging pages
   - Update map when date range changes

---

### Phase 9: Vehicle Control Page ✅
**Duration**: ~5 hours

1. **Create Vehicle Control Components**
   ```svelte
   <!-- ChargeControl.svelte -->
   <script lang="ts">
     import { Switch } from '$lib/components/ui/switch';
     import { createMutation } from '@tanstack/svelte-query';

     export let vin: string;
     export let isCharging: boolean;

     const toggleCharge = createMutation({
       mutationFn: (charge: boolean) =>
         apiRequest(`/vehicles/${vin}/charge`, {
           method: 'POST',
           body: JSON.stringify({ charge })
         })
     });
   </script>

   <div class="flex items-center gap-2">
     <Switch
       checked={isCharging}
       onCheckedChange={(val) => $toggleCharge.mutate(val)}
     />
     <span>Charge Now</span>
   </div>
   ```

2. **Control Features**
   - Charge now (on/off)
   - Preconditioning (on/off)
   - Charge schedule (hour picker)
   - Wakeup vehicle (button)
   - Horn (button with count)
   - Lights (button with duration)
   - Door locks (lock/unlock)

3. **Multi-Vehicle Support**
   - Tabs for each vehicle
   - Per-vehicle control state

4. **Real-time Status Updates**
   - Poll vehicle status every 30 seconds
   - Show battery level, charging status, position

---

### Phase 10: Configuration Pages ✅
**Duration**: ~4 hours

1. **Config Hub Page**
   - Links to all config sections
   - Current settings display

2. **OAuth Setup Flow**
   - Brand selector (Peugeot, Opel, Citroën, DS, Vauxhall)
   - Email, password, country code inputs
   - Form validation with Superforms + Zod
   - Submit → redirect to OAuth URL

   ```typescript
   // Zod schema
   import { z } from 'zod';

   export const loginSchema = z.object({
     brand: z.enum(['Peugeot', 'Opel', 'Citroën', 'DS', 'Vauxhall']),
     email: z.string().email(),
     password: z.string().min(1),
     countryCode: z.string().length(2)
   });
   ```

3. **OTP Verification**
   - "Send SMS" button
   - SMS code input
   - PIN input
   - Submit and redirect

4. **Settings Management**
   - Currency selector
   - Export format (CSV/Excel)
   - Minimum trip length
   - ABRP integration toggle

---

### Phase 11: Log Viewer ✅
**Duration**: ~2 hours

1. **Create Log Display Component**
   ```svelte
   <script lang="ts">
     import { createQuery } from '@tanstack/svelte-query';

     const logsQuery = createQuery({
       queryKey: ['logs'],
       queryFn: () => apiRequest<string[]>('/logs'),
       refetchInterval: 5000  // Auto-refresh every 5s
     });
   </script>

   <div class="h-[600px] overflow-y-auto bg-black text-green-400 p-4 font-mono text-sm">
     {#if $logsQuery.data}
       {#each $logsQuery.data as line}
         <div>{line}</div>
       {/each}
     {/if}
   </div>
   ```

2. **Auto-scroll to Bottom**
   - Scroll to latest log entry
   - Pause auto-scroll if user scrolls up

---

### Phase 12: Polish & Optimization ✅
**Duration**: ~4 hours

1. **Loading States**
   - Skeleton loaders for tables and charts
   - Spinner for button actions
   - Progress bars for data fetching

2. **Error Handling**
   - Toast notifications for errors
   - Error boundaries for components
   - Retry failed requests

3. **Responsive Design**
   - Mobile-first approach
   - Hamburger menu for mobile
   - Touch-friendly controls

4. **Performance**
   - Code splitting per route
   - Lazy load charts
   - Virtual scrolling for large tables
   - Memoize expensive calculations

5. **Accessibility**
   - Keyboard navigation
   - ARIA labels
   - Focus management
   - Screen reader support

---

### Phase 13: Testing & Deployment ✅
**Duration**: ~3 hours

1. **Test All Features**
   - Manual testing of each page
   - Test OAuth flow end-to-end
   - Test remote control commands
   - Test data export
   - Test on mobile devices

2. **Build Production Bundle**
   ```bash
   cd frontend
   npm run build
   ```

3. **Serve from Flask**
   ```python
   # web/app.py
   from flask import Flask, send_from_directory

   app = Flask(__name__, static_folder='../frontend/build')

   @app.route('/')
   @app.route('/<path:path>')
   def serve_frontend(path=''):
       return send_from_directory(app.static_folder, 'index.html')
   ```

4. **Deploy**
   - Test production build locally
   - Deploy to server
   - Monitor for errors

---

## 📊 Component Mapping: Dash → SvelteKit

| Dash Component | SvelteKit Equivalent |
|----------------|---------------------|
| `dbc.Card` | `<Card>` (shadcn) |
| `dbc.Button` | `<Button>` (shadcn) |
| `dcc.Dropdown` | `<Select>` (shadcn) |
| `dcc.Input` | `<Input>` (shadcn) |
| `dcc.RangeSlider` | `<Slider>` (shadcn) |
| `dash_table.DataTable` | TanStack Table |
| `dcc.Graph` (Plotly) | Chart.js + svelte-chartjs |
| `dbc.Tabs` | `<Tabs>` (shadcn) |
| `dbc.Modal` | `<Dialog>` (shadcn) |
| `dbc.Alert` | `<Alert>` (shadcn) |
| `dcc.Loading` | Custom spinner + skeleton |
| `dcc.Store` | Svelte stores |
| `@callback` | TanStack Query + mutations |
| `clientside_callback` | Reactive statements (`$:`) |

---

## 🔑 Key Implementation Details

### Date Range Filtering
```typescript
// src/lib/stores/filters.ts
import { writable, derived } from 'svelte/store';

export const dateRange = writable<[Date, Date]>([
  new Date('2020-01-01'),
  new Date()
]);

export const filteredTrips = derived(
  [tripsStore, dateRange],
  ([$trips, $range]) =>
    $trips.filter(trip =>
      trip.start_at >= $range[0] && trip.start_at <= $range[1]
    )
);
```

### Reactive Summary Calculations
```svelte
<script lang="ts">
  import { filteredTrips } from '$lib/stores/filters';

  $: avgConsumption = $filteredTrips.reduce((sum, t) =>
    sum + t.consumption_km, 0
  ) / $filteredTrips.length;

  $: totalCost = $filteredTrips.reduce((sum, t) =>
    sum + (t.consumption_km * electricityPrice), 0
  );
</script>

<SummaryCard
  title="Average Consumption"
  value={avgConsumption.toFixed(2)}
  unit="kWh/100km"
/>
```

### Data Export
```typescript
// src/lib/utils/export.ts
import { saveAs } from 'file-saver';

export function exportToCSV(data: any[], filename: string) {
  const headers = Object.keys(data[0]);
  const csv = [
    headers.join(','),
    ...data.map(row =>
      headers.map(h => JSON.stringify(row[h])).join(',')
    )
  ].join('\n');

  const blob = new Blob([csv], { type: 'text/csv' });
  saveAs(blob, `${filename}.csv`);
}
```

---

## 🎨 Design System

### Color Palette (Tailwind)
```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',      // Blue
        success: '#10b981',      // Green
        warning: '#f59e0b',      // Yellow
        danger: '#ef4444',       // Red
        muted: '#6b7280'         // Gray
      }
    }
  }
}
```

### Typography
- Headings: `font-bold text-2xl` to `text-4xl`
- Body: `text-base`
- Small: `text-sm text-muted-foreground`

---

## ⚡ Performance Targets

- First Contentful Paint: < 1.5s
- Time to Interactive: < 3s
- Lighthouse Score: > 90
- Bundle Size: < 300KB (gzipped)

---

## 🔒 Security Considerations

1. **API Authentication**
   - Add JWT tokens for API requests
   - Store tokens in httpOnly cookies
   - CSRF protection

2. **Input Validation**
   - Zod schemas for all forms
   - Server-side validation in Flask

3. **XSS Prevention**
   - Svelte automatically escapes HTML
   - Use `{@html}` sparingly

---

## 📝 Migration Checklist

- [ ] Phase 1: Project Setup
- [ ] Phase 2: Backend API Refactor
- [ ] Phase 3: Core Layout & Navigation
- [ ] Phase 4: Authentication & State Management
- [ ] Phase 5: Dashboard Page
- [ ] Phase 6: Trips Page
- [ ] Phase 7: Charging Page
- [ ] Phase 8: Map Page
- [ ] Phase 9: Vehicle Control Page
- [ ] Phase 10: Configuration Pages
- [ ] Phase 11: Log Viewer
- [ ] Phase 12: Polish & Optimization
- [ ] Phase 13: Testing & Deployment

---

## 📚 Resources

- [SvelteKit Docs](https://kit.svelte.dev/docs)
- [shadcn-svelte](https://www.shadcn-svelte.com/)
- [TanStack Query](https://tanstack.com/query/latest/docs/svelte/overview)
- [Chart.js](https://www.chartjs.org/)
- [Mapbox GL JS](https://docs.mapbox.com/mapbox-gl-js/)
- [Tailwind CSS](https://tailwindcss.com/)

---

## 🎯 Success Criteria

✅ All existing features migrated and working
✅ Modern, responsive UI with shadcn-svelte
✅ Type-safe with TypeScript
✅ Fast performance (< 3s TTI)
✅ Maintainable codebase
✅ Mobile-friendly
✅ Accessible (WCAG AA)

---

**Estimated Total Time**: ~45-50 hours

**Recommended Approach**: Start with Phase 1-4 to get the foundation right, then build pages incrementally (one phase per day).