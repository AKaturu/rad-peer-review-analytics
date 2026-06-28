from rad_peer_review_analytics.importer import import_csv


class TestImportCSV:
    SIMPLE_CSV = """review_id,reviewer_id,reviewee_id,case_id,score
R1,R001,R002,C001,1
R2,R001,R003,C002,3b
"""

    def test_basic_import(self):
        result = import_csv(self.SIMPLE_CSV)
        assert len(result.rows) == 2
        assert result.skipped == 0
        assert result.errors == []

    def test_import_values(self):
        result = import_csv(self.SIMPLE_CSV)
        r1 = result.rows[0]
        assert r1.review_id == "R1"
        assert r1.reviewer_id == "R001"
        assert r1.reviewee_id == "R002"
        assert r1.score == "1"
        assert r1.score_system == "radpeer"

        r2 = result.rows[1]
        assert r2.score == "3b"

    def test_standard_score_system(self):
        csv_text = """review_id,reviewer_id,reviewee_id,case_id,score,score_system
R1,R001,R002,C001,agree,standard
"""
        result = import_csv(csv_text)
        assert result.rows[0].score_system == "standard"
        assert result.rows[0].score == "agree"

    def test_flexible_column_names_pascal(self):
        csv_text = """ReviewID,ReviewerID,RevieweeID,CaseID,Score
R1,R001,R002,C001,1
"""
        result = import_csv(csv_text)
        assert len(result.rows) == 1
        assert result.rows[0].review_id == "R1"
        assert result.rows[0].reviewer_id == "R001"

    def test_flexible_column_names_mixed(self):
        csv_text = """ReviewerId,RevieweeId,review_id,case_id,score
R001,R002,R1,C001,1
"""
        result = import_csv(csv_text)
        assert result.rows[0].reviewer_id == "R001"
        assert result.rows[0].reviewee_id == "R002"

    def test_missing_required_fields_skipped(self):
        csv_text = """review_id,reviewer_id,reviewee_id,case_id,score
R1,,R002,C001,1
R2,R001,R003,C002,
"""
        result = import_csv(csv_text)
        assert result.skipped == 2
        assert len(result.errors) == 2

    def test_date_format_ymd(self):
        csv_text = """review_id,reviewer_id,reviewee_id,case_id,score,review_date
R1,R001,R002,C001,1,2024-06-15
"""
        result = import_csv(csv_text)
        from datetime import date

        assert result.rows[0].review_date == date(2024, 6, 15)

    def test_date_format_mdy(self):
        csv_text = """review_id,reviewer_id,reviewee_id,case_id,score,review_date
R1,R001,R002,C001,1,06/15/2024
"""
        result = import_csv(csv_text)
        from datetime import date

        assert result.rows[0].review_date == date(2024, 6, 15)

    def test_invalid_date_ignored(self):
        csv_text = """review_id,reviewer_id,reviewee_id,case_id,score,review_date
R1,R001,R002,C001,1,not-a-date
"""
        result = import_csv(csv_text)
        assert result.rows[0].review_date is None

    def test_additional_fields(self):
        csv_text = (
            "review_id,reviewer_id,reviewee_id,case_id,score,"
            "modality,body_part,finding_type,comment\n"
            "R1,R001,R002,C001,1,CT,CHEST,nodule,Good study\n"
        )
        result = import_csv(csv_text)
        r = result.rows[0]
        assert r.modality == "CT"
        assert r.body_part == "CHEST"
        assert r.finding_type == "nodule"
        assert r.comment == "Good study"

    def test_pascal_case_additional_fields(self):
        csv_text = (
            "ReviewID,ReviewerID,RevieweeID,CaseID,Score,"
            "Modality,BodyPart,FindingType,Comment\n"
            "R1,R001,R002,C001,1,CT,CHEST,nodule,test\n"
        )
        result = import_csv(csv_text)
        assert result.rows[0].modality == "CT"

    def test_empty_csv(self):
        csv_text = """review_id,reviewer_id,reviewee_id,case_id,score
"""
        result = import_csv(csv_text)
        assert len(result.rows) == 0
        assert result.skipped == 0
