# Implementation Plan: Split Handlers into Separate Files

## Goal
Refactor the codebase by splitting the large `handlers_user.py` and `handlers_admin.py` files into smaller, domain-specific modules. This will make the code easier to maintain, read, and extend.

## Proposed Changes
I propose creating a new `handlers/` directory and organizing the files by feature:

### `handlers/user/` (User Handlers)
1. **`user_core.py`**: Basic commands (`/start`, back to main), subscription checking, checking balance, and contact admin.
2. **`user_purchase.py`**: Everything related to buying a number (selecting country, pagination, confirming purchase, and fetching SMS codes).
3. **`user_deposit.py`**: Handling user deposit requests and receiving payment screenshots.

### `handlers/admin/` (Admin Handlers)
1. **`admin_core.py`**: Main admin panel view, bot statistics, and broadcast messaging.
2. **`admin_users.py`**: Viewing users, adding/subtracting balance, and banning/unbanning.
3. **`admin_catalog.py`**: Managing countries (adding/removing, setting prices), mandatory channels, and bot card settings.
4. **`admin_deposits.py`**: Viewing pending deposits and initiating deposit confirmations.
5. **`admin_text_handler.py`**: The central processor for admin text inputs (processing the specific states like entering amounts, channel links, or IDs).

### `bot.py`
- Update `bot.py` to import all these handlers from the new modular structure and register them accordingly.
- The `handlers_user.py` and `handlers_admin.py` files in the root directory will be **deleted** after the migration.

## User Review Required
> [!IMPORTANT]
> Please review the proposed file structure. Is this breakdown granular enough, or would you prefer a different organization? Let me know if you approve this structure so I can proceed with the refactoring.

## Verification Plan
1. Move the code into the new files.
2. Update imports across all files.
3. Start the bot and verify that no import errors occur.
4. Simulate basic text messages and callbacks to ensure the routing remains intact.
