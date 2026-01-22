"""Tests for CLI commands."""

import pytest
import json
from click.testing import CliRunner
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from cli import cli


class TestSearchCommand:
    """Test search command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch('cli.execute_search')
    @patch('cli.format_products')
    def test_search_basic(self, mock_format, mock_execute):
        """Test basic search command."""
        mock_execute.return_value = [Mock()]

        result = self.runner.invoke(cli, ['search', 'laptop'])

        assert result.exit_code == 0
        mock_execute.assert_called_once()
        mock_format.assert_called_once()

        # Verify params passed to execute_search
        call_args = mock_execute.call_args[0][0]
        assert call_args['keyword_search'] == 'laptop'

    @patch('cli.execute_search')
    @patch('cli.format_products')
    @patch('cli.find_category')
    def test_search_with_category(self, mock_find_cat, mock_execute, mock_format):
        """Test search with category option."""
        mock_cat = Mock()
        mock_cat.value = '30'
        mock_find_cat.return_value = mock_cat
        mock_execute.return_value = [Mock()]

        result = self.runner.invoke(cli, ['search', 'laptop', '--category', 'computers'])

        assert result.exit_code == 0
        mock_find_cat.assert_called_once_with('computers')

    @patch('cli.execute_search')
    @patch('cli.format_products')
    @patch('cli.find_location')
    def test_search_with_location(self, mock_find_loc, mock_execute, mock_format):
        """Test search with location option."""
        mock_loc = Mock()
        mock_loc.value = '43'
        mock_find_loc.return_value = mock_loc
        mock_execute.return_value = [Mock()]

        result = self.runner.invoke(cli, ['search', 'laptop', '--location', 'TX_Austin'])

        assert result.exit_code == 0
        mock_find_loc.assert_called_once_with('TX_Austin')

    @patch('cli.execute_search')
    @patch('cli.format_products')
    def test_search_with_price_range(self, mock_format, mock_execute):
        """Test search with price range."""
        mock_execute.return_value = [Mock()]

        result = self.runner.invoke(cli, [
            'search', 'laptop',
            '--min-price', '100',
            '--max-price', '500'
        ])

        assert result.exit_code == 0
        call_args = mock_execute.call_args[0][0]
        assert call_args['low_price'] == 100
        assert call_args['high_price'] == 500

    @patch('cli.execute_search')
    @patch('cli.format_products')
    def test_search_with_format_option(self, mock_format, mock_execute):
        """Test search with different output formats."""
        from unittest.mock import ANY

        mock_products = [Mock()]
        mock_execute.return_value = mock_products

        for fmt in ['table', 'json', 'quiet']:
            mock_format.reset_mock()
            result = self.runner.invoke(cli, ['search', 'laptop', '--format', fmt])
            assert result.exit_code == 0
            # Verify format was called with correct format type
            assert mock_format.call_count == 1
            call_args = mock_format.call_args[0]
            assert call_args[1] == fmt

    @patch('cli.find_category')
    def test_search_invalid_category(self, mock_find_cat):
        """Test search with invalid category."""
        mock_find_cat.side_effect = ValueError("Category not found")

        result = self.runner.invoke(cli, ['search', 'laptop', '--category', 'invalid'])

        assert result.exit_code != 0
        assert "Category not found" in result.output

    @patch('cli.execute_search')
    def test_search_execution_error(self, mock_execute):
        """Test search with execution error."""
        mock_execute.side_effect = Exception("Search failed")

        result = self.runner.invoke(cli, ['search', 'laptop'])

        assert result.exit_code != 0
        assert "Search failed" in result.output


class TestCreateCommand:
    """Test create command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch('cli.create_search_config')
    def test_create_basic(self, mock_create):
        """Test basic create command."""
        mock_create.return_value = Path('/fake/path/test.json')

        result = self.runner.invoke(cli, ['create', 'test-search'])

        assert result.exit_code == 0
        mock_create.assert_called_once_with('test-search', {}, interactive=True)
        assert "Saved search created" in result.output

    @patch('cli.create_search_config')
    def test_create_with_invalid_name(self, mock_create):
        """Test create with invalid name."""
        mock_create.side_effect = ValueError("Invalid search name")

        result = self.runner.invoke(cli, ['create', 'bad/name'])

        assert result.exit_code != 0
        assert "Invalid search name" in result.output


class TestEditCommand:
    """Test edit command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch('cli.edit_search_config')
    def test_edit_basic(self, mock_edit):
        """Test basic edit command."""
        result = self.runner.invoke(cli, ['edit', 'test-search'])

        assert result.exit_code == 0
        mock_edit.assert_called_once_with('test-search')
        assert "updated" in result.output

    @patch('cli.edit_search_config')
    def test_edit_not_found(self, mock_edit):
        """Test editing non-existent search."""
        mock_edit.side_effect = FileNotFoundError("Saved search 'test' not found")

        result = self.runner.invoke(cli, ['edit', 'nonexistent'])

        assert result.exit_code != 0
        assert "not found" in result.output


class TestListCommand:
    """Test list command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch('cli.list_search_configs')
    @patch('cli.get_saved_searches_dir')
    def test_list_with_configs(self, mock_get_dir, mock_list):
        """Test listing existing configs."""
        mock_get_dir.return_value = Path('/fake/path')
        mock_list.return_value = ['search1', 'search2', 'search3']

        result = self.runner.invoke(cli, ['list'])

        assert result.exit_code == 0
        assert 'search1' in result.output
        assert 'search2' in result.output
        assert 'search3' in result.output
        assert 'Total: 3' in result.output

    @patch('cli.list_search_configs')
    def test_list_empty(self, mock_list):
        """Test listing when no configs exist."""
        mock_list.return_value = []

        result = self.runner.invoke(cli, ['list'])

        assert result.exit_code == 0
        assert 'No saved searches found' in result.output


class TestDeleteCommand:
    """Test delete command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch('cli.delete_search_config')
    def test_delete_with_yes_flag(self, mock_delete):
        """Test delete with --yes flag."""
        result = self.runner.invoke(cli, ['delete', 'test-search', '--yes'])

        assert result.exit_code == 0
        mock_delete.assert_called_once_with('test-search')
        assert 'Deleted' in result.output

    @patch('cli.delete_search_config')
    def test_delete_with_confirmation(self, mock_delete):
        """Test delete with interactive confirmation."""
        result = self.runner.invoke(cli, ['delete', 'test-search'], input='y\n')

        assert result.exit_code == 0
        mock_delete.assert_called_once_with('test-search')

    @patch('cli.delete_search_config')
    def test_delete_cancelled(self, mock_delete):
        """Test delete cancelled by user."""
        result = self.runner.invoke(cli, ['delete', 'test-search'], input='n\n')

        assert result.exit_code == 0
        mock_delete.assert_not_called()
        assert 'Cancelled' in result.output

    @patch('cli.delete_search_config')
    def test_delete_not_found(self, mock_delete):
        """Test deleting non-existent search."""
        mock_delete.side_effect = FileNotFoundError("Saved search 'test' not found")

        result = self.runner.invoke(cli, ['delete', 'nonexistent', '--yes'])

        assert result.exit_code != 0
        assert "not found" in result.output


class TestRunCommand:
    """Test run command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch('cli.execute_search_from_file')
    @patch('cli.format_products')
    @patch('cli.get_search_config_path')
    def test_run_single_search(self, mock_get_path, mock_format, mock_execute):
        """Test running single saved search."""
        mock_get_path.return_value = Path('/fake/path/test.json')
        mock_execute.return_value = [Mock()]

        result = self.runner.invoke(cli, ['run', 'test-search'])

        assert result.exit_code == 0
        mock_execute.assert_called_once()
        mock_format.assert_called_once()
        assert 'Running saved search: test-search' in result.output

    @patch('cli.execute_search_from_file')
    @patch('cli.format_products')
    @patch('cli.list_search_configs')
    @patch('cli.get_search_config_path')
    def test_run_all_searches(self, mock_get_path, mock_list, mock_format, mock_execute):
        """Test running all saved searches."""
        mock_list.return_value = ['search1', 'search2']
        mock_get_path.side_effect = [
            Path('/fake/search1.json'),
            Path('/fake/search2.json')
        ]
        mock_execute.return_value = [Mock()]

        result = self.runner.invoke(cli, ['run', '--all'])

        assert result.exit_code == 0
        assert mock_execute.call_count == 2
        assert 'Running: search1' in result.output
        assert 'Running: search2' in result.output

    @patch('cli.list_search_configs')
    def test_run_all_with_no_searches(self, mock_list):
        """Test running all when no searches exist."""
        mock_list.return_value = []

        result = self.runner.invoke(cli, ['run', '--all'])

        assert result.exit_code == 0
        assert 'No saved searches found' in result.output

    @patch('cli.execute_search_from_file')
    @patch('cli.get_search_config_path')
    def test_run_search_not_found(self, mock_get_path, mock_execute):
        """Test running non-existent search."""
        mock_get_path.return_value = Path('/fake/nonexistent.json')
        mock_execute.side_effect = FileNotFoundError()

        result = self.runner.invoke(cli, ['run', 'nonexistent'])

        assert result.exit_code != 0
        assert "not found" in result.output

    def test_run_without_arguments(self):
        """Test run command without name or --all."""
        result = self.runner.invoke(cli, ['run'])

        assert result.exit_code != 0
        assert "Specify a search name or use --all" in result.output

    @patch('cli.execute_search_from_file')
    @patch('cli.format_products')
    @patch('cli.list_search_configs')
    @patch('cli.get_search_config_path')
    def test_run_all_continues_on_error(self, mock_get_path, mock_list, mock_format, mock_execute):
        """Test that run --all continues even if one search fails."""
        mock_list.return_value = ['search1', 'search2']
        mock_get_path.side_effect = [
            Path('/fake/search1.json'),
            Path('/fake/search2.json')
        ]
        # First search fails, second succeeds
        mock_execute.side_effect = [Exception("Failed"), [Mock()]]

        result = self.runner.invoke(cli, ['run', '--all'])

        # Should complete with exit code 0
        assert result.exit_code == 0
        # Both searches should be attempted
        assert mock_execute.call_count == 2
        assert 'Failed' in result.output


class TestListCategoriesCommand:
    """Test list-categories command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch('cli.list_categories')
    def test_list_categories_all(self, mock_list):
        """Test listing all categories."""
        mock_list.return_value = [
            ('Computers', '30'),
            ('Electronics', '7'),
            ('Books', '15')
        ]

        result = self.runner.invoke(cli, ['list-categories'])

        assert result.exit_code == 0
        assert 'Computers' in result.output
        assert 'Electronics' in result.output
        assert 'Books' in result.output
        assert 'Total: 3' in result.output

    @patch('cli.list_categories')
    def test_list_categories_with_filter(self, mock_list):
        """Test listing categories with filter."""
        mock_list.return_value = [('Computers', '30')]

        result = self.runner.invoke(cli, ['list-categories', '--filter', 'computer'])

        assert result.exit_code == 0
        mock_list.assert_called_once_with('computer')
        assert 'Computers' in result.output

    @patch('cli.list_categories')
    def test_list_categories_no_matches(self, mock_list):
        """Test listing categories with filter that matches nothing."""
        mock_list.return_value = []

        result = self.runner.invoke(cli, ['list-categories', '--filter', 'xyz123'])

        assert result.exit_code == 0
        assert 'No categories found' in result.output


class TestListLocationsCommand:
    """Test list-locations command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch('cli.list_locations')
    def test_list_locations_all(self, mock_list):
        """Test listing all locations."""
        mock_list.return_value = [
            ('TX_Austin', '43'),
            ('CA_SanFrancisco', '12'),
            ('NY_NewYork', '25')
        ]

        result = self.runner.invoke(cli, ['list-locations'])

        assert result.exit_code == 0
        assert 'TX_Austin' in result.output
        assert 'CA_SanFrancisco' in result.output
        assert 'NY_NewYork' in result.output
        assert 'Total: 3' in result.output

    @patch('cli.list_locations')
    def test_list_locations_with_filter(self, mock_list):
        """Test listing locations with filter."""
        mock_list.return_value = [('TX_Austin', '43')]

        result = self.runner.invoke(cli, ['list-locations', '--filter', 'TX'])

        assert result.exit_code == 0
        mock_list.assert_called_once_with('TX')
        assert 'TX_Austin' in result.output

    @patch('cli.list_locations')
    def test_list_locations_no_matches(self, mock_list):
        """Test listing locations with filter that matches nothing."""
        mock_list.return_value = []

        result = self.runner.invoke(cli, ['list-locations', '--filter', 'xyz123'])

        assert result.exit_code == 0
        assert 'No locations found' in result.output


class TestCLIGroup:
    """Test CLI group and general functionality."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_cli_help(self):
        """Test CLI help text."""
        result = self.runner.invoke(cli, ['--help'])

        assert result.exit_code == 0
        assert 'GoodWill Shopping Search' in result.output

    def test_cli_version(self):
        """Test CLI version option."""
        result = self.runner.invoke(cli, ['--version'])

        assert result.exit_code == 0
        assert '1.0.0' in result.output

    def test_search_help(self):
        """Test search command help."""
        result = self.runner.invoke(cli, ['search', '--help'])

        assert result.exit_code == 0
        assert 'Quick search without saving' in result.output

    def test_invalid_command(self):
        """Test invoking invalid command."""
        result = self.runner.invoke(cli, ['invalid-command'])

        assert result.exit_code != 0


class TestIntegration:
    """Test integration scenarios."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch('cli.execute_search')
    @patch('cli.format_products')
    @patch('cli.find_category')
    @patch('cli.find_location')
    def test_full_search_workflow(self, mock_find_loc, mock_find_cat, mock_format, mock_execute):
        """Test complete search with all options."""
        mock_cat = Mock()
        mock_cat.value = '30'
        mock_find_cat.return_value = mock_cat

        mock_loc = Mock()
        mock_loc.value = '43'
        mock_find_loc.return_value = mock_loc

        mock_execute.return_value = [Mock(), Mock()]

        result = self.runner.invoke(cli, [
            'search', 'laptop',
            '--category', 'computers',
            '--location', 'austin',
            '--min-price', '100',
            '--max-price', '500',
            '--format', 'json',
            '--page-size', '20'
        ])

        assert result.exit_code == 0

        # Verify all parameters were passed
        call_args = mock_execute.call_args[0][0]
        assert call_args['keyword_search'] == 'laptop'
        assert call_args['categories'] == '30'
        assert call_args['good_will_location'] == '43'
        assert call_args['low_price'] == 100
        assert call_args['high_price'] == 500
        assert call_args['page_size'] == 20

        # Verify format was called with correct format type
        assert mock_format.call_count == 1
        call_args = mock_format.call_args[0]
        assert call_args[1] == 'json'

    @patch('cli.create_search_config')
    @patch('cli.list_search_configs')
    @patch('cli.execute_search_from_file')
    @patch('cli.format_products')
    @patch('cli.get_search_config_path')
    @patch('cli.delete_search_config')
    def test_create_run_delete_workflow(self, mock_delete, mock_get_path,
                                       mock_format, mock_execute, mock_list, mock_create):
        """Test complete workflow: create, run, delete."""
        # Create
        mock_create.return_value = Path('/fake/test.json')
        result = self.runner.invoke(cli, ['create', 'test'])
        assert result.exit_code == 0

        # List (should show the created search)
        mock_list.return_value = ['test']
        result = self.runner.invoke(cli, ['list'])
        assert result.exit_code == 0
        assert 'test' in result.output

        # Run
        mock_get_path.return_value = Path('/fake/test.json')
        mock_execute.return_value = [Mock()]
        result = self.runner.invoke(cli, ['run', 'test'])
        assert result.exit_code == 0

        # Delete
        result = self.runner.invoke(cli, ['delete', 'test', '--yes'])
        assert result.exit_code == 0
