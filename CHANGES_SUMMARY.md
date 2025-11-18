# Changes Summary - Fix for CSV Data Updates

## Problem
When changing names/addresses in the CSV file, the system was returning `None` instead of extracting the new data with AI.

## Root Cause
The pipeline was checking if an entry existed in the database, and if it did (even with `None` values), it would skip AI extraction in some cases.

## Solution

### 1. Enhanced `get_existing_result()` in `db_manager.py`
- Now returns `None` if both `recipient_name` and `address` are `None` or empty
- This ensures entries with missing data trigger AI extraction
- Added proper string validation to check for empty strings

### 2. Improved Pipeline Logic in `data_pipeline.py`
- **Before**: Would sometimes skip entries that existed in database
- **After**: Only skips AI extraction if BOTH name AND address exist and are valid
- If an entry exists but has `None` values, it will be processed with AI
- Better error handling and status messages

### 3. Better Error Handling
- Distinguishes between "AI (Failed)" (extraction error) and "AI (No Data)" (no data found)
- Doesn't save `None` values on complete failures (allows retry)
- Saves `None` values only when AI completes but finds no data

### 4. Added Compatibility Functions
- `extract_name_address()` - Alias for `extract_with_ai()`
- `get_label()` - Alias for `get_existing_result()`
- `save_label()` - Alias for `save_result()`

## How It Works Now

1. **CSV Sync**: `refresh_database_from_csv()` adds new entries from CSV to database (with `None` values)
2. **Database Check**: For each CSV entry, check if it exists in database with valid data
3. **AI Extraction**: If entry doesn't exist OR has `None`/empty values, extract with AI
4. **Save Results**: Save extracted data to database (updates existing entries or creates new ones)
5. **Output**: Write results to output CSV

## Key Behavior

- ✅ New entries in CSV → Processed with AI
- ✅ Entries with `None` values → Processed with AI  
- ✅ Entries with valid data → Used from database (skips AI for speed)
- ✅ Changed raw_text in CSV → Treated as new entry → Processed with AI
- ✅ Failed extractions → Can be retried on next run

## Testing

To test the fix:

1. Add a new entry to `ocr_raw_labels.csv`
2. Run: `python main.py`
3. Verify the new entry is extracted with AI
4. Change an existing entry's raw_text in CSV
5. Run again and verify it's treated as new and extracted

## Files Modified

- `db_manager.py`: Enhanced `get_existing_result()` and added alias functions
- `data_pipeline.py`: Improved logic to handle `None` values properly
- `ai_extractor.py`: Added `extract_name_address()` alias function
- `optimize_for_speed.py`: Fixed reference to non-existent function

