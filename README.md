# BidBuddy-QA-Automation

This repo contains the QA automation framework for BidBuddy.

---

BidBuddy - QA Onboarding Guide
Welcome to BidBuddy! This guide will give you everything you need to understand the product, its users, and how to test it effectively.

# BidBuddy UI Automation Framework

We are building a frontend automation framework for BidBuddy.

Tech Stack:
- Python
- Playwright
- Pytest

Focus:
- Scalable structure
- Reusable components
- Clean architecture

What is BidBuddy?
BidBuddy is a platform that helps property management companies make better, faster, and less risky decisions when selecting vendors for maintenance work.

Today, when a property manager needs work done (roofing, plumbing, HVAC, etc.), they send out Requests for Proposals (RFPs) to vendors, receive bids back, and then have to manually compare those bids in spreadsheets. Bids come in different formats, with different scopes, and it's easy to miss hidden fees, scope gaps, or unfair comparisons.

BidBuddy fixes this by:

Structuring the bidding process - Guided RFP creation, organized vendor invitations, and centralized bid tracking
AI-powered bid comparison - Automatically normalizing bids into an apples-to-apples comparison table, highlighting discrepancies and missing scope items
Bid leveling - A guided process to send clarification requests to vendors and get revised bids until all bids are comparable
Vendor scoring - Weighted scoring criteria so property managers can evaluate vendors objectively

The tagline: "Your Bids. Your Buddy. Your Budget."


The Two Sides of BidBuddy
BidBuddy has two completely separate user experiences based on organization type. When you log in, you'll see one or the other — never both.
1. Property Manager Side
Who they are: Property management companies that manage properties and maintenance for their client companies (building owners, HOAs, investment groups, etc.).

What they do:

Manage a portfolio of properties (addresses, photos, details, notes)
Create RFPs (Requests for Proposals) when a property needs maintenance work
Invite vendors to bid on those RFPs
Review, compare, and level bids using the RFP Manager
Award the winning bid to a vendor
Communicate with vendors via chat throughout the process

Key concept - Teams: Property managers can manage multiple client companies. Each client company is a "Team" in BidBuddy. Users can switch between teams using a toggle at the top of the app. When you switch teams, you see different properties, RFPs, and bids — everything is scoped to the active team.

URL pattern: /dashboard/property-manager/*

Navigation menu:

Dashboard (home/overview)
Properties
RFPs
Bids
Messages (chat)
Teams (management)
2. Vendor Side
Who they are: Service providers — roofing companies, plumbers, HVAC contractors, electricians, etc.

What they do:

Receive bid invitations from property managers
Review RFP details and ask clarifying questions via chat
Submit bids with pricing and scope
Respond to clarification requests during the leveling process
Receive award/non-award notifications

Key differences from Property Managers:

Vendors do NOT sign up on their own — they are invited by a property manager
Vendors have a single team (their company), no team switching
Vendors do NOT pay for BidBuddy — it's free for them
Vendors do NOT create RFPs or manage properties

URL pattern: /dashboard/vendor/*

Navigation menu:

Dashboard
Chat
Teams


The Core Workflow
Here's how the two sides interact, end to end:

1. PM creates a property in BidBuddy
         ↓
2. PM creates an RFP for that property (multi-step wizard)
   - Selects property and trade type (roofing, plumbing, etc.)
   - Enters scope details, due dates, descriptions
   - Invites vendors to bid
         ↓
3. Vendors receive invitations (eventually via email)
   - They can accept ("Will Bid") or decline ("Will Not Bid")
         ↓
4. Vendors submit their bids
   - Upload proposal documents with pricing
         ↓
5. PM reviews bids in the RFP Manager
   - Bids Tab: See all submitted bids, amounts, statuses
   - Compare & Level Tab: AI-generated comparison table
     (unlocked when 2+ bids are received)
         ↓
6. PM identifies discrepancies and sends clarification requests
   - Vendors respond and submit updated bids
   - Comparison table updates automatically
         ↓
7. PM scores and awards the winning bid
         ↓
8. Notifications sent to all vendors (awarded / not awarded)


Key Features to Test
Authentication & Registration
Area  -> What to test
Login  ->  Sign in with email/password
Registration  ->  Create a new account
Organization type  ->  After login, user should be redirected to the correct dashboard (PM or Vendor) based on their org type
Route guards  ->  PM users shouldn't be able to access /dashboard/vendor/* and vice versa
Unauthenticated access  ->  Visiting any /dashboard/* URL while logged out should redirect to login

Properties (Property Manager Only)
Properties represent physical locations that a PM's clients own.

Area  ->  What to test
Property List  ->  View all properties as cards with images; empty state when none exist
Create Property  ->  Multi-section form: name, address (with Mapbox autocomplete), property type, details, photos, notes
Property Detail  ->  View property info, photo carousel, map, notes, associated RFPs
Edit Property  ->  Inline editing: hover over sections to reveal edit button; edit notes, photos (drag to reorder), property details, address
Delete Property  ->  Kebab menu → Delete → "Type DELETE to confirm" dialog (currently shows "coming soon")
Team Scoping  ->  Switching teams should show different properties


Address autocomplete notes:

Uses Mapbox — type a street address and suggestions appear
Selecting an address auto-fills city, state, ZIP
Known limitation: abbreviations mid-query (e.g., "N 19th") may not return results; type full words ("North 19th")
Create RFP Modal (Property Manager Only)
A 5-step wizard accessed from the Properties page or RFP list.

Step
What to test
1. Property & Trade Type
Select a property from the dropdown; choose "Single Trade" or "Multi-Trade"
2. Select Trades
Pick trade categories (roofing, plumbing, HVAC, etc.)
3. RFP Details
Title, bid due date, estimated start date, per-trade scope descriptions (min 10 chars each)
4. Invite Vendors
Select vendors to invite (currently shows all vendors in system)
5. Review & Submit
Review all entered info; submit creates the RFP


Validation rules:

Bid due date must be on or before estimated start date
Each selected trade must have a description (min 10 characters)
Property and trade type are required before proceeding

Side effects on submit:

A placeholder bid is created for each invited vendor (status: INVITED)
A chat room is created for PM ↔ Vendor communication per vendor
RFP Manager (Property Manager Only)
The workspace for managing an individual RFP's lifecycle.

Area
What to test
Bids Tab -> 
List of all bids with amounts, statuses, dates
Compare & Level Tab -> 
AI-generated comparison table (requires 2+ bids)
Invite Vendors -> 
Can invite additional vendors after RFP creation
Copilot Sidebar -> 
AI assistant panel on the right side

Chat / Messages
Area
What to test
Chat rooms -> 
Each RFP + vendor pair has its own chat room
Messaging ->
Send and receive messages between PM and vendor
Navigation -> 
Deep links to specific chat rooms should work

Team Switching (Property Manager Only)
Area
What to test
Team toggle -> 
Switching teams at the top of the app
Data refresh -> 
Properties, RFPs, and bids should change when team switches
Detail page redirect -> 
If you're on a property/RFP detail page and switch teams, you should be redirected to the list view
List page stays -> 
If you're on a list page and switch teams, you should stay on the list with new data


Terminology Quick Reference
Term
Definition
RFP
Request for Proposal — a formal request from a PM to vendors asking them to submit bids for work
Bid
A vendor's response to an RFP — includes pricing, scope, and proposal details
Trade
A category of work (e.g., Roofing, Plumbing, HVAC, Electrical, Gutters)
Single-Trade RFP
An RFP for one type of work
Multi-Trade RFP
An RFP covering multiple types of work
Leveling
The process of normalizing bids so they cover the same scope and can be compared fairly
Discrepancy
A difference found between bids — could be a missing scope item, price outlier, or vendor-specific addition
Scope Item
An individual line item of work (e.g., "Remove existing shingles", "Install ice barrier")
Team
For PMs: represents a client company. For vendors: just their single company.
Organization
The top-level entity — the PM company or vendor company itself
Copilot
The AI assistant sidebar in the RFP Manager
Comparison Table
AI-generated side-by-side view of all vendor bids, organized by scope item



Environment & Access
To be filled in by the team:

App URL: https://dev.bidbuddy.com/auth/sign-in?returnTo=%2Fproperty-manager%2Fproperties
How to switch teams: Click the team name/dropdown at the top of the sidebar


Tips for Effective Testing
Always test both sides — Log in as a PM and as a Vendor to see both perspectives of the same action
Test team switching early — Many bugs hide in data not refreshing when teams change
Check empty states — What does the app show when there are no properties? No RFPs? No bids?
Test the form wizard carefully — Try going back and forth between steps, changing selections, and verifying validation
Watch for stale data — After creating/editing/deleting something, does the list/detail view update?
Check route guards — Try manually typing vendor URLs while logged in as a PM (and vice versa)
Note "Coming Soon" placeholders — Document them but don't file bugs for them; they're known incomplete features


