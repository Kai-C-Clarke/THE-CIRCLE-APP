# Quick Reference - Essential Files for Catherine's Version

## 3 Critical Fixes (Must Have)

### 1. PDF Generator
**File:** `pdf_generator_fixed_column.py` → `pdf_generator.py`  
**Fixes:** Column name + PIL import + aspect ratios  
**Test:** Generate PDF, check images display correctly

### 2. Universal Categorization  
**File:** `utils_universal.py` → `utils.py`  
**Fixes:** Age-aware categories (reads birth date from DB)  
**Also:** Update app.py line 186: `categorize_memory(text, year=year)`  
**Test:** Add memory for 30-year-old at work → should be "work" not "education"

### 3. Flask Send File
**File:** Edit existing `app.py` around line 724  
**Change:**
```python
# Add these 3 parameters:
return send_file(
    pdf_path,
    as_attachment=True,
    download_name=filename,  # ADD THIS
    mimetype='application/pdf'  # ADD THIS
)
```
**Test:** Generate PDF, should download without error

---

## Optional Enhancements

### 4. Clean UI (One Export Button)
**File:** `index_PROPER_FIX.html` → `templates/index.html`  
**What:** Removes 2 redundant PDF buttons  
**Test:** Export page shows only "Family Album" card

### 5. AI Photo Matching (Future)
**Files:** 
- Add `ai_photo_matcher.py` (new file)
- Add `test_ai_matching.py` (new file)
- Add AI routes to `app.py` (86 lines)
- Run DB migration (memory_media table)

**Test:** `python3 test_ai_matching.py`

---

## Installation Order

```bash
# 1. Backup everything first
cp pdf_generator.py pdf_generator_backup.py
cp utils.py utils_backup.py
cp app.py app_backup.py
cp templates/index.html templates/index_backup.html

# 2. Apply essential fixes
cp ~/Downloads/pdf_generator_fixed_column.py pdf_generator.py
cp ~/Downloads/utils_universal.py utils.py
# Edit app.py: Fix send_file (line 724) + categorize call (line 186)

# 3. Test
python3 app.py
# Generate PDF - should work
# Add memory - category should be correct

# 4. Optional: Clean UI
cp ~/Downloads/index_PROPER_FIX.html templates/index.html

# 5. Optional: AI features (later)
cp ~/Downloads/ai_photo_matcher.py .
cp ~/Downloads/test_ai_matching.py .
# Add routes to app.py
# Run DB migration
```

---

## Files You Have Ready

✓ `pdf_generator_fixed_column.py`  
✓ `utils_universal.py`  
✓ `app_with_ai_complete.py` (reference for app.py changes)  
✓ `index_PROPER_FIX.html`  
✓ `ai_photo_matcher.py`  
✓ `test_ai_matching.py`  
✓ `fix_sendfile.py` (auto-fix script)  

All in ~/Downloads, ready to apply to Catherine's version.

---

## What Works Now in Test Bed

✅ PDFs generate with correct images  
✅ Categories age-aware (any user)  
✅ One clean export button  
✅ AI photo matching ready (needs testing)  

Sleep well!
