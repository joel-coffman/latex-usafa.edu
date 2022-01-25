# Course Evaluation Reports

Instructions to generate course evaluation reports:

1. Create a CSV with course enrollment by section: RIOS > Course > Course
   Enrollment Sections
2. Sanitize feedback in Microsoft Excel spreadsheet:
   - Replace `.` with `` (for NaN)
3. Export feedback to CSV
4. Update DF data in script
5. Execute `./evaluations.py`
6. Run `make` in the reports directory
