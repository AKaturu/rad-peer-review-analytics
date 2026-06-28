from typer.testing import CliRunner

from rad_peer_review_analytics.cli import app

runner = CliRunner()


class TestDemoCommand:
    def test_demo_default(self):
        result = runner.invoke(app, ["demo"])
        assert result.exit_code == 0
        assert "Summary" in result.stdout
        assert "reviews" in result.stdout

    def test_demo_custom_counts(self):
        result = runner.invoke(app, ["demo", "--reviewers", "3", "--reviews", "10"])
        assert result.exit_code == 0
        assert "10 reviews" in result.stdout

    def test_demo_standard_system(self):
        result = runner.invoke(app, ["demo", "--system", "standard", "--reviews", "10"])
        assert result.exit_code == 0

    def test_demo_no_load(self):
        result = runner.invoke(app, ["demo", "--no-load", "--reviews", "5"])
        assert result.exit_code == 0


class TestAnalyzeCommand:
    def test_analyze_without_data_fails(self):
        result = runner.invoke(app, ["analyze"])
        assert result.exit_code == 1
        assert "No review data loaded" in result.stderr

    def test_analyze_after_demo(self):
        result = runner.invoke(app, ["demo", "--reviews", "10"])
        assert result.exit_code == 0
        result = runner.invoke(app, ["analyze"])
        assert result.exit_code == 0
        assert "Peer Review Analytics Report" in result.stdout


class TestReviewersCommand:
    def test_reviewers_without_data_fails(self):
        result = runner.invoke(app, ["reviewers"])
        assert result.exit_code == 1

    def test_reviewers_after_demo(self):
        runner.invoke(app, ["demo", "--reviews", "10"])
        result = runner.invoke(app, ["reviewers"])
        assert result.exit_code == 0
        assert "Reviewer Statistics" in result.stdout


class TestModalitiesCommand:
    def test_modalities_without_data_fails(self):
        result = runner.invoke(app, ["modalities"])
        assert result.exit_code == 1

    def test_modalities_after_demo(self):
        runner.invoke(app, ["demo", "--reviews", "10"])
        result = runner.invoke(app, ["modalities"])
        assert result.exit_code == 0
        assert "Modality Statistics" in result.stdout


class TestTrendsCommand:
    def test_trends_without_data_fails(self):
        result = runner.invoke(app, ["trends"])
        assert result.exit_code == 1

    def test_trends_after_demo(self):
        runner.invoke(app, ["demo", "--reviews", "10"])
        result = runner.invoke(app, ["trends"])
        assert result.exit_code == 0
        assert "Monthly Trends" in result.stdout


class TestExportCommand:
    def test_export_without_data_fails(self):
        result = runner.invoke(app, ["export", "out.csv"])
        assert result.exit_code == 1

    def test_export_after_demo(self):
        import os
        import tempfile

        runner.invoke(app, ["demo", "--reviews", "10"])
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "out.csv")
            result = runner.invoke(app, ["export", path])
            assert result.exit_code == 0
            assert "Exported" in result.stdout
            assert os.path.exists(path)


class TestReportCommand:
    def test_report_without_data_fails(self):
        result = runner.invoke(app, ["report"])
        assert result.exit_code == 1

    def test_report_after_demo(self):
        runner.invoke(app, ["demo", "--reviews", "10"])
        result = runner.invoke(app, ["report"])
        assert result.exit_code == 0
        assert "Peer Review Analytics Report" in result.stdout

    def test_report_with_csv_export(self):
        import os
        import tempfile

        runner.invoke(app, ["demo", "--reviews", "10"])
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "report.csv")
            result = runner.invoke(app, ["report", "--output", path])
            assert result.exit_code == 0
            assert os.path.exists(f"{os.path.splitext(path)[0]}_reviewers.csv")

    def test_report_with_json_export(self):
        import os
        import tempfile

        runner.invoke(app, ["demo", "--reviews", "10"])
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "report.json")
            result = runner.invoke(app, ["report", "--json", path])
            assert result.exit_code == 0
            assert os.path.exists(path)


class TestImportReviewsCommand:
    def test_import_missing_file(self):
        result = runner.invoke(app, ["import-reviews", "nonexistent.csv"])
        assert result.exit_code != 0

    def test_import_valid_csv(self):
        import os
        import tempfile

        csv_content = "review_id,reviewer_id,reviewee_id,case_id,score\nR1,R001,R002,C001,1\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "test.csv")
            with open(path, "w") as f:
                f.write(csv_content)
            result = runner.invoke(app, ["import-reviews", path])
            assert result.exit_code == 0
            assert "Imported" in result.stdout
