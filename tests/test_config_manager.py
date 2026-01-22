"""Tests for config manager functions."""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, call
from GoodWillShoppingSearch.utils.config_manager import (
    get_saved_searches_dir,
    get_search_config_path,
    create_search_config,
    edit_search_config,
    delete_search_config,
    list_search_configs,
    get_search_config,
    _prompt_for_search_params
)


class TestGetSavedSearchesDir:
    """Test get_saved_searches_dir function."""

    def test_get_saved_searches_dir_returns_path(self):
        """Test that function returns a Path object."""
        result = get_saved_searches_dir()
        assert isinstance(result, Path)

    def test_get_saved_searches_dir_ends_with_saved_searches(self):
        """Test that path ends with 'saved_searches'."""
        result = get_saved_searches_dir()
        assert result.name == 'saved_searches'

    def test_get_saved_searches_dir_is_consistent(self):
        """Test that function returns same path on multiple calls."""
        path1 = get_saved_searches_dir()
        path2 = get_saved_searches_dir()
        assert path1 == path2


class TestGetSearchConfigPath:
    """Test get_search_config_path function."""

    def test_get_search_config_path_basic(self):
        """Test basic path generation."""
        result = get_search_config_path("test-search")
        assert isinstance(result, Path)
        assert result.name == "test-search.json"

    def test_get_search_config_path_different_names(self):
        """Test that different names produce different paths."""
        path1 = get_search_config_path("search1")
        path2 = get_search_config_path("search2")
        assert path1 != path2
        assert path1.name == "search1.json"
        assert path2.name == "search2.json"

    def test_get_search_config_path_parent_dir(self):
        """Test that parent directory is saved_searches."""
        result = get_search_config_path("test")
        assert result.parent.name == 'saved_searches'


class TestCreateSearchConfig:
    """Test create_search_config function."""

    def test_create_search_config_basic(self, tmp_path, monkeypatch):
        """Test creating a basic search config."""
        # Temporarily change saved_searches directory to tmp_path
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        params = {'keyword_search': 'laptop', 'categories': '7'}
        result = create_search_config('test-search', params)

        assert result.exists()
        assert result.name == 'test-search.json'

        # Verify JSON content
        with open(result, 'r') as f:
            data = json.load(f)
        assert data['keyword_search'] == 'laptop'
        assert data['categories'] == '7'

    def test_create_search_config_missing_keyword(self, tmp_path, monkeypatch):
        """Test that missing keyword_search raises ValueError."""
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        params = {'categories': '7'}
        with pytest.raises(ValueError, match="keyword_search is required"):
            create_search_config('test', params)

    def test_create_search_config_invalid_name_with_slash(self, tmp_path, monkeypatch):
        """Test that name with slash raises ValueError."""
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        params = {'keyword_search': 'test'}
        with pytest.raises(ValueError, match="Invalid search name"):
            create_search_config('test/bad', params)

    def test_create_search_config_invalid_name_with_backslash(self, tmp_path, monkeypatch):
        """Test that name with backslash raises ValueError."""
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        params = {'keyword_search': 'test'}
        with pytest.raises(ValueError, match="Invalid search name"):
            create_search_config('test\\bad', params)

    def test_create_search_config_invalid_name_with_dotdot(self, tmp_path, monkeypatch):
        """Test that name with .. raises ValueError."""
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        params = {'keyword_search': 'test'}
        with pytest.raises(ValueError, match="Invalid search name"):
            create_search_config('../bad', params)

    def test_create_search_config_empty_name(self, tmp_path, monkeypatch):
        """Test that empty name raises ValueError."""
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        params = {'keyword_search': 'test'}
        with pytest.raises(ValueError, match="Invalid search name"):
            create_search_config('', params)

    def test_create_search_config_creates_directory(self, tmp_path, monkeypatch):
        """Test that directory is created if it doesn't exist."""
        saves_dir = tmp_path / 'new_saves'
        assert not saves_dir.exists()

        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: saves_dir
        )

        params = {'keyword_search': 'laptop'}
        create_search_config('test', params)

        assert saves_dir.exists()
        assert saves_dir.is_dir()

    def test_create_search_config_full_params(self, tmp_path, monkeypatch):
        """Test creating config with all parameters."""
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        params = {
            'keyword_search': 'computer',
            'categories': '7',
            'good_will_location': '43',
            'low_price': '100',
            'high_price': '500',
            'show_buy_now_only': True
        }
        result = create_search_config('full-search', params)

        with open(result, 'r') as f:
            data = json.load(f)

        assert data == params

    @patch('GoodWillShoppingSearch.utils.config_manager._prompt_for_search_params')
    def test_create_search_config_interactive(self, mock_prompt, tmp_path, monkeypatch):
        """Test interactive config creation."""
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        mock_prompt.return_value = {'keyword_search': 'laptop', 'categories': '30'}

        result = create_search_config('interactive', {}, interactive=True)

        mock_prompt.assert_called_once()
        assert result.exists()

        with open(result, 'r') as f:
            data = json.load(f)
        assert data['keyword_search'] == 'laptop'


class TestEditSearchConfig:
    """Test edit_search_config function."""

    def create_test_config(self, tmp_path, name, params):
        """Helper to create a test config file."""
        config_file = tmp_path / f"{name}.json"
        with open(config_file, 'w') as f:
            json.dump(params, f)
        return config_file

    @patch('GoodWillShoppingSearch.utils.config_manager._prompt_for_search_params')
    @patch('click.echo')
    def test_edit_search_config_basic(self, mock_echo, mock_prompt, tmp_path, monkeypatch):
        """Test editing an existing config."""
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        # Create initial config
        initial_params = {'keyword_search': 'old', 'categories': '7'}
        self.create_test_config(tmp_path, 'test', initial_params)

        # Mock updated params
        updated_params = {'keyword_search': 'new', 'categories': '30'}
        mock_prompt.return_value = updated_params

        # Edit config
        edit_search_config('test')

        # Verify updated
        config_path = tmp_path / 'test.json'
        with open(config_path, 'r') as f:
            data = json.load(f)
        assert data == updated_params

    def test_edit_search_config_not_found(self, tmp_path, monkeypatch):
        """Test editing non-existent config raises error."""
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        with pytest.raises(FileNotFoundError, match="Saved search .* not found"):
            edit_search_config('nonexistent')

    @patch('GoodWillShoppingSearch.utils.config_manager._prompt_for_search_params')
    @patch('click.echo')
    def test_edit_search_config_preserves_file(self, mock_echo, mock_prompt, tmp_path, monkeypatch):
        """Test that edit preserves the same file."""
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        initial_params = {'keyword_search': 'test'}
        config_file = self.create_test_config(tmp_path, 'test', initial_params)
        original_mtime = config_file.stat().st_mtime

        mock_prompt.return_value = {'keyword_search': 'updated'}

        # Wait a tiny bit to ensure mtime would change if file was rewritten
        import time
        time.sleep(0.01)

        edit_search_config('test')

        # File should exist at same path
        assert config_file.exists()


class TestDeleteSearchConfig:
    """Test delete_search_config function."""

    def create_test_config(self, tmp_path, name):
        """Helper to create a test config file."""
        config_file = tmp_path / f"{name}.json"
        config_file.write_text('{"keyword_search": "test"}')
        return config_file

    def test_delete_search_config_basic(self, tmp_path, monkeypatch):
        """Test deleting a config."""
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        config_file = self.create_test_config(tmp_path, 'test')
        assert config_file.exists()

        delete_search_config('test')

        assert not config_file.exists()

    def test_delete_search_config_not_found(self, tmp_path, monkeypatch):
        """Test deleting non-existent config raises error."""
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        with pytest.raises(FileNotFoundError, match="Saved search .* not found"):
            delete_search_config('nonexistent')


class TestListSearchConfigs:
    """Test list_search_configs function."""

    def test_list_search_configs_empty(self, tmp_path, monkeypatch):
        """Test listing when no configs exist."""
        saves_dir = tmp_path / 'empty_saves'
        saves_dir.mkdir()

        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: saves_dir
        )

        result = list_search_configs()
        assert result == []

    def test_list_search_configs_no_directory(self, tmp_path, monkeypatch):
        """Test listing when directory doesn't exist."""
        nonexistent_dir = tmp_path / 'nonexistent'

        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: nonexistent_dir
        )

        result = list_search_configs()
        assert result == []

    def test_list_search_configs_single_file(self, tmp_path, monkeypatch):
        """Test listing with single config file."""
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        (tmp_path / 'test.json').write_text('{}')

        result = list_search_configs()
        assert result == ['test']

    def test_list_search_configs_multiple_files(self, tmp_path, monkeypatch):
        """Test listing with multiple config files."""
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        (tmp_path / 'search1.json').write_text('{}')
        (tmp_path / 'search2.json').write_text('{}')
        (tmp_path / 'search3.json').write_text('{}')

        result = list_search_configs()
        assert len(result) == 3
        assert set(result) == {'search1', 'search2', 'search3'}

    def test_list_search_configs_sorted(self, tmp_path, monkeypatch):
        """Test that results are sorted alphabetically."""
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        (tmp_path / 'zebra.json').write_text('{}')
        (tmp_path / 'apple.json').write_text('{}')
        (tmp_path / 'banana.json').write_text('{}')

        result = list_search_configs()
        assert result == ['apple', 'banana', 'zebra']

    def test_list_search_configs_ignores_non_json(self, tmp_path, monkeypatch):
        """Test that non-JSON files are ignored."""
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        (tmp_path / 'valid.json').write_text('{}')
        (tmp_path / 'readme.txt').write_text('text')
        (tmp_path / 'data.xml').write_text('<xml/>')

        result = list_search_configs()
        assert result == ['valid']


class TestGetSearchConfig:
    """Test get_search_config function."""

    def test_get_search_config_basic(self, tmp_path, monkeypatch):
        """Test getting a config."""
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        params = {'keyword_search': 'laptop', 'categories': '30'}
        config_file = tmp_path / 'test.json'
        with open(config_file, 'w') as f:
            json.dump(params, f)

        result = get_search_config('test')
        assert result == params

    def test_get_search_config_not_found(self, tmp_path, monkeypatch):
        """Test getting non-existent config raises error."""
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        with pytest.raises(FileNotFoundError, match="Saved search .* not found"):
            get_search_config('nonexistent')

    def test_get_search_config_full_params(self, tmp_path, monkeypatch):
        """Test getting config with all parameters."""
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        params = {
            'keyword_search': 'computer',
            'categories': '7',
            'good_will_location': '43',
            'low_price': '100',
            'high_price': '500',
            'show_buy_now_only': True,
            'show_one_cent_ship_only': False
        }
        config_file = tmp_path / 'full.json'
        with open(config_file, 'w') as f:
            json.dump(params, f)

        result = get_search_config('full')
        assert result == params


class TestIntegration:
    """Test integration scenarios."""

    def test_create_list_get_delete_workflow(self, tmp_path, monkeypatch):
        """Test complete CRUD workflow."""
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        # Create
        params = {'keyword_search': 'laptop'}
        create_search_config('test', params)

        # List
        configs = list_search_configs()
        assert 'test' in configs

        # Get
        retrieved = get_search_config('test')
        assert retrieved == params

        # Delete
        delete_search_config('test')

        # List again
        configs = list_search_configs()
        assert 'test' not in configs

    def test_multiple_configs_independent(self, tmp_path, monkeypatch):
        """Test that multiple configs don't interfere."""
        monkeypatch.setattr(
            'GoodWillShoppingSearch.utils.config_manager.get_saved_searches_dir',
            lambda: tmp_path
        )

        params1 = {'keyword_search': 'laptop'}
        params2 = {'keyword_search': 'desktop'}

        create_search_config('search1', params1)
        create_search_config('search2', params2)

        # Verify both exist independently
        assert get_search_config('search1') == params1
        assert get_search_config('search2') == params2

        # Delete one
        delete_search_config('search1')

        # Other should still exist
        assert get_search_config('search2') == params2
        with pytest.raises(FileNotFoundError):
            get_search_config('search1')


class TestPromptForSearchParams:
    """Test _prompt_for_search_params function."""

    @patch('click.confirm')
    @patch('click.prompt')
    def test_prompt_minimal_params(self, mock_prompt, mock_confirm):
        """Test prompting with minimal input."""
        # Setup mocks
        mock_prompt.side_effect = [
            'laptop',  # keyword_search
            '',        # category (empty)
            ''         # location (empty)
        ]
        mock_confirm.side_effect = [False, False, False]  # No price range, no buy now, no one cent ship

        result = _prompt_for_search_params()

        assert result['keyword_search'] == 'laptop'
        assert 'categories' not in result
        assert 'good_will_location' not in result

    @patch('click.confirm')
    @patch('click.prompt')
    @patch('GoodWillShoppingSearch.utils.enum_utils.find_category')
    def test_prompt_with_category(self, mock_find_cat, mock_prompt, mock_confirm):
        """Test prompting with category."""
        mock_cat = Mock()
        mock_cat.value = '30'
        mock_find_cat.return_value = mock_cat

        mock_prompt.side_effect = [
            'laptop',       # keyword_search
            'computers',    # category
            ''              # location (empty)
        ]
        mock_confirm.side_effect = [False, False, False]

        result = _prompt_for_search_params()

        assert result['keyword_search'] == 'laptop'
        assert result['categories'] == '30'

    @patch('click.confirm')
    @patch('click.prompt')
    @patch('GoodWillShoppingSearch.utils.enum_utils.find_location')
    def test_prompt_with_location(self, mock_find_loc, mock_prompt, mock_confirm):
        """Test prompting with location."""
        mock_loc = Mock()
        mock_loc.value = '43'
        mock_find_loc.return_value = mock_loc

        mock_prompt.side_effect = [
            'laptop',     # keyword_search
            '',           # category (empty)
            'TX_Austin'   # location
        ]
        mock_confirm.side_effect = [False, False, False]

        result = _prompt_for_search_params()

        assert result['keyword_search'] == 'laptop'
        assert result['good_will_location'] == '43'

    @patch('click.confirm')
    @patch('click.prompt')
    def test_prompt_with_price_range(self, mock_prompt, mock_confirm):
        """Test prompting with price range."""
        mock_prompt.side_effect = [
            'laptop',  # keyword_search
            '',        # category (empty)
            '',        # location (empty)
            100,       # low_price
            500        # high_price
        ]
        mock_confirm.side_effect = [True, False, False]  # Yes to price range

        result = _prompt_for_search_params()

        assert result['keyword_search'] == 'laptop'
        assert result['low_price'] == 100
        assert result['high_price'] == 500

    @patch('click.confirm')
    @patch('click.prompt')
    def test_prompt_with_buy_now_only(self, mock_prompt, mock_confirm):
        """Test prompting with buy now only option."""
        mock_prompt.side_effect = [
            'laptop',  # keyword_search
            '',        # category (empty)
            ''         # location (empty)
        ]
        mock_confirm.side_effect = [False, True, False]  # Yes to buy now only

        result = _prompt_for_search_params()

        assert result['keyword_search'] == 'laptop'
        assert result['show_buy_now_only'] is True

    @patch('click.confirm')
    @patch('click.prompt')
    def test_prompt_with_one_cent_ship(self, mock_prompt, mock_confirm):
        """Test prompting with one cent shipping option."""
        mock_prompt.side_effect = [
            'laptop',  # keyword_search
            '',        # category (empty)
            ''         # location (empty)
        ]
        mock_confirm.side_effect = [False, False, True]  # Yes to one cent ship

        result = _prompt_for_search_params()

        assert result['keyword_search'] == 'laptop'
        assert result['show_one_cent_ship_only'] is True

    @patch('click.confirm')
    @patch('click.prompt')
    def test_prompt_with_existing_params(self, mock_prompt, mock_confirm):
        """Test prompting with existing params as defaults."""
        existing = {
            'keyword_search': 'old_keyword',
            'categories': '7',
            'low_price': '50',
            'high_price': '250'
        }

        mock_prompt.side_effect = [
            'new_keyword',  # keyword_search (override)
            '',             # category (empty)
            ''              # location (empty)
        ]
        mock_confirm.side_effect = [False, False, False]

        result = _prompt_for_search_params(existing)

        assert result['keyword_search'] == 'new_keyword'

    @patch('click.echo')
    @patch('click.confirm')
    @patch('click.prompt')
    @patch('GoodWillShoppingSearch.utils.enum_utils.find_category')
    def test_prompt_with_invalid_category(self, mock_find_cat, mock_prompt, mock_confirm, mock_echo):
        """Test prompting with invalid category shows warning."""
        mock_find_cat.side_effect = ValueError("Category not found")

        mock_prompt.side_effect = [
            'laptop',         # keyword_search
            'invalid_cat',    # category (invalid)
            ''                # location (empty)
        ]
        mock_confirm.side_effect = [False, False, False]

        result = _prompt_for_search_params()

        # Should still return result but without category
        assert result['keyword_search'] == 'laptop'
        assert 'categories' not in result
        # Warning should be echoed
        mock_echo.assert_called()

    @patch('click.echo')
    @patch('click.confirm')
    @patch('click.prompt')
    @patch('GoodWillShoppingSearch.utils.enum_utils.find_location')
    def test_prompt_with_invalid_location(self, mock_find_loc, mock_prompt, mock_confirm, mock_echo):
        """Test prompting with invalid location shows warning."""
        mock_find_loc.side_effect = ValueError("Location not found")

        mock_prompt.side_effect = [
            'laptop',         # keyword_search
            '',               # category (empty)
            'invalid_loc'     # location (invalid)
        ]
        mock_confirm.side_effect = [False, False, False]

        result = _prompt_for_search_params()

        # Should still return result but without location
        assert result['keyword_search'] == 'laptop'
        assert 'good_will_location' not in result
        # Warning should be echoed
        mock_echo.assert_called()
