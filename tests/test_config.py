"""Tests for novus_pytils.config."""

from pathlib import Path

import pytest
import yaml

from novus_pytils import config


class TestLoadSave:
    def test_yaml_round_trip_keeps_order(self, tmp_path: Path) -> None:
        data = {"zeta": 1, "alpha": {"list": ["a", "b"], "flag": True}, "name": "héllo"}
        p = config.save_config(data, tmp_path / "d" / "c.yaml")
        assert config.load_config(p) == data
        assert p.read_text().startswith("zeta: 1\nalpha:\n")
        assert "héllo" in p.read_text()

    def test_json_round_trip(self, tmp_path: Path) -> None:
        data = {"a": 1, "b": {"c": [1, 2]}}
        p = config.save_config(data, tmp_path / "c.json")
        assert config.load_config(p) == data
        assert p.read_text().endswith("}\n")

    def test_empty_yaml_is_empty_dict(self, tmp_path: Path) -> None:
        p = tmp_path / "e.yml"
        p.write_text("")
        assert config.load_config(p) == {}
        assert config.load_yaml(p) is None

    def test_rejects_wrong_extension_and_non_mapping(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="yaml"):
            config.load_config(tmp_path / "c.toml")
        with pytest.raises(ValueError, match="yaml"):
            config.save_config({}, tmp_path / "c.ini")
        p = tmp_path / "list.yaml"
        p.write_text("- a\n- b\n")
        with pytest.raises(ValueError, match="mapping"):
            config.load_config(p)

    def test_invalid_yaml_raises(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.yaml"
        p.write_text("key: [unclosed")
        with pytest.raises(yaml.YAMLError):
            config.load_config(p)

    def test_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            config.load_config(tmp_path / "nope.yaml")


class TestDottedKeys:
    def test_get_value(self) -> None:
        data = {"db": {"host": "h", "opts": {"timeout": 3}}, "items": [1, 2]}
        assert config.get_value(data, "db.host") == "h"
        assert config.get_value(data, "db.opts.timeout") == 3
        assert config.get_value(data, "items") == [1, 2]
        assert config.get_value(data, "db.nope") is None
        assert config.get_value(data, "items.0", default="d") == "d"  # lists aren't descended
        assert config.get_value(data, "db.host.deeper", default=0) == 0

    def test_set_value(self) -> None:
        data: dict = {"db": {"host": "h"}}
        config.set_value(data, "db.host", "new")
        config.set_value(data, "db.port", 5432)
        config.set_value(data, "a.b.c", "deep")
        assert data == {"db": {"host": "new", "port": 5432}, "a": {"b": {"c": "deep"}}}
        with pytest.raises(TypeError):
            config.set_value(data, "db.host.x", 1)

    def test_missing_keys(self) -> None:
        data = {"a": {"b": None}, "c": 1}
        assert config.missing_keys(data, ["a.b", "c", "d", "a.x"]) == ["d", "a.x"]


class TestMerge:
    def test_merge_configs_deep_and_non_destructive(self) -> None:
        base = {"db": {"host": "l", "port": 1}, "items": [1], "x": 1}
        over = {"db": {"host": "r", "timeout": 9}, "items": [2], "y": 2}
        merged = config.merge_configs(base, over)
        assert merged == {
            "db": {"host": "r", "port": 1, "timeout": 9},
            "items": [2],
            "x": 1,
            "y": 2,
        }
        assert base["db"] == {"host": "l", "port": 1}
        assert config.merge_configs() == {}
        assert config.merge_configs({"a": 1}, {"a": {"b": 1}}, {"a": {"c": 2}}) == {
            "a": {"b": 1, "c": 2}
        }
