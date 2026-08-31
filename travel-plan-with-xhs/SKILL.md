---
name: travel-plan-with-xhs
description: Create practical travel plans from user priorities, Xiaohongshu travel notes, and current transport or hotel checks. Use when planning a trip that should combine social travel experience with verifiable booking information; do not use for booking or purchasing travel.
---

# Travel Plan With XHS

Create an actionable trip plan that separates subjective travel experience from facts that must be current. The goal is a plan a traveller can book and follow, not a list of attractions.

## Confirm the trip brief

Extract answers already given. Ask only for missing decisions that materially change the route. Confirm these before researching:

| Required decision | Why it changes the plan |
|---|---|
| Dates and nights | Determines transport availability, hotel dates, opening times, and pacing. |
| Departure city and party size | Determines viable transport and room count. |
| Transport preference | Determines whether the route should optimize comfort, time, price, self-drive, or public transport. |

Also capture budget tier, destination choice, traveller constraints (children, mobility, food preferences), visa status for international trips, and pace preference when they are relevant. If the user supplied enough information, start research without repeating questions.

## Research in two evidence layers

Keep these layers visibly separate in notes and in the final plan.

### Experience layer: Xiaohongshu and traveller notes

Use user-supplied Xiaohongshu links first. When accessible, extract:

- title, creator, publication date if visible, and engagement metrics if visible;
- route order, recommended time of day, photo points, food or hotel suggestions, and warnings from the note body and images;
- comments only when the user supplies their public text or screenshots.

Prioritize high-save/high-like notes as reading order only. Do not treat engagement as proof that a price, opening time, queue estimate, or venue status is current.

Do not request, accept, store, or use login cookies, passwords, verification codes, private browser data, or other account credentials. Do not bypass login, paywalls, rate limits, or anti-bot controls. If a note cannot be accessed publicly, label it `unread` and continue with accessible sources; never claim that it was read.

### Fact layer: official and booking sources

Verify booking and time-sensitive facts using primary sources where possible:

- railway timetable, fare, sale date, and availability: 12306;
- flights: airline official sites first; use Ctrip, Fliggy, Trip.com, or similar only for comparison;
- hotels: the property's official page or a major booking platform using the exact stay dates and occupancy;
- visa, entry rules, ticket prices, reservations, closures: relevant official authority or venue.

Record the query date, exact travel date, occupancy, source, and whether a price is live, indicative, or unavailable. Never present a different date's fare as the user's fare. If exact future inventory is not saleable yet, give a clearly labeled reference range and the precise next check date.

## Build the plan

1. Compare destination or transport alternatives only if the user has not yet chosen one. Make the trade-off explicit: door-to-door time, comfort, price, booking risk, and trip time lost.
2. Choose a base hotel area first. Minimize unnecessary hotel changes and cross-city travel.
3. Group sights by geography and schedule high-demand reservations at their actual available times. Put weather-sensitive or low-priority stops in flexible slots.
4. For every day provide: departure window, ordered route, realistic transit buffer, meal suggestion, evening choice, and a rain/crowding fallback.
5. Budget for the stated party size, with line items for transport, accommodation, local transport, food, tickets, and contingency. Give both total and per-person amounts.
6. Add an action timeline: when tickets go on sale, when free cancellation ends, when reservations open, and what needs reconfirming.

## Final delivery

Deliver an HTML trip guide when the user asks for a readable plan or file. It must be a self-contained, mobile-readable document and include:

- trip snapshot and assumptions;
- booking recommendation and alternatives;
- hotel shortlist with exact location, room type, date/occupancy basis, and price status;
- day-by-day route with Plan B;
- transport, reservation, packing, and crowding notes as applicable;
- total and per-person budget; and
- source table separating `experience sources` from `verified facts`, including unread Xiaohongshu links.

Use direct links for sources. Do not copy long note text or image text. State uncertainties beside the affected item rather than hiding them in a generic disclaimer.

## Quality gate

Before delivery, check:

- every booking recommendation matches the requested dates, travellers, and direction;
- no social note is represented as an official fact;
- each timed day is geographically coherent and leaves realistic buffers;
- all temporary price information has a query date and booking status; and
- each inaccessible source is marked unread rather than inferred.
