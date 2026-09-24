"""Several learners on one computer, each with their own data.

Owner, 09-24: "add user creation if they want to switch users, and each user
has his own data, make it smooth and clean".
"""
from __future__ import annotations

import pytest
from PySide6.QtCore import QCoreApplication, QEvent

from conftest import pump

from operators_console.core import paths, profiles
from operators_console.core.storage import Store


def test_the_first_profile_is_the_existing_data_folder(isolated_home):
    assert paths.active_profile() == paths.DEFAULT_PROFILE
    assert paths.data_dir() == paths.root_dir()
    assert [p.id for p in profiles.profiles()] == [paths.DEFAULT_PROFILE]


def test_a_new_profile_gets_its_own_folder(isolated_home):
    ada = profiles.create("Ada Lovelace")
    assert ada.id == "ada-lovelace"
    assert paths.profile_dir(ada.id).is_dir()
    assert paths.profile_dir(ada.id) != paths.root_dir()
    assert [p.name for p in profiles.profiles()][-1] == "Ada Lovelace"


def test_names_must_be_present_and_unique(isolated_home):
    profiles.create("Sam")
    with pytest.raises(ValueError):
        profiles.create("sam")
    with pytest.raises(ValueError):
        profiles.create("   ")


def test_each_profile_has_separate_progress(isolated_home):
    main = Store()
    main.set_setting("learner_name", "Main")
    main.close()
    other = profiles.create("Other")
    profiles.switch(other.id)
    second = Store()
    assert second.setting("learner_name", "") == ""
    second.set_setting("learner_name", "Other")
    second.close()
    profiles.switch(paths.DEFAULT_PROFILE)
    back = Store()
    assert back.setting("learner_name", "") == "Main"
    back.close()


def test_the_open_profile_is_remembered(isolated_home):
    other = profiles.create("Other")
    profiles.switch(other.id)
    paths.set_active_profile(None)          # as if the app restarted
    assert paths.active_profile() == other.id


def test_a_missing_profile_folder_falls_back_to_the_main_one(isolated_home):
    other = profiles.create("Gone")
    profiles.switch(other.id)
    import shutil
    shutil.rmtree(paths.profile_dir(other.id))
    paths.set_active_profile(None)
    assert paths.active_profile() == paths.DEFAULT_PROFILE


def test_removing_moves_the_data_aside(isolated_home):
    other = profiles.create("Temp")
    (paths.profile_dir(other.id) / "marker.txt").write_text("x")
    parked = profiles.remove(other.id)
    assert "removed-profiles" in parked
    assert (paths.root_dir() / "removed-profiles").is_dir()
    assert other.id not in [p.id for p in profiles.profiles()]


def test_the_main_and_the_open_profile_cannot_be_removed(isolated_home):
    with pytest.raises(ValueError):
        profiles.remove(paths.DEFAULT_PROFILE)
    other = profiles.create("Busy")
    profiles.switch(other.id)
    with pytest.raises(ValueError):
        profiles.remove(other.id)


def test_rename(isolated_home):
    other = profiles.create("Old name")
    profiles.rename(other.id, "New name")
    assert profiles.profiles()[-1].name == "New name"


def test_the_update_files_stay_in_the_root(isolated_home):
    """Profiles must not scatter update downloads and the lock."""
    import inspect
    from operators_console.core import updates
    assert "paths.data_dir()" not in inspect.getsource(updates)


def _destroy(window, qt_app):
    window.close()
    window.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete.value)
    pump(qt_app)


def test_switching_reopens_the_window_on_the_other_profile(qt_app,
                                                           isolated_home):
    from operators_console import app as app_module
    first = app_module._new_window(qt_app)
    first.ctx.store.set_setting("onboarded", True)
    first.ctx.store.set_setting("learner_name", "Main")
    shown = [first]
    onboarded = []
    switch = app_module.profile_switcher(qt_app, shown, onboarded.append)
    other = profiles.create("Second")
    assert switch(other.id)
    pump(qt_app)
    assert shown[0] is not first
    assert shown[0].ctx.store.setting("learner_name", "") == ""
    assert onboarded == [shown[0]]          # a new profile gets set up
    assert switch(paths.DEFAULT_PROFILE)
    pump(qt_app)
    assert shown[0].ctx.store.setting("learner_name", "") == "Main"
    _destroy(shown[0], qt_app)


def test_the_file_menu_lists_profiles(qt_app, window, isolated_home):
    profiles.create("Second")
    window._fill_profile_menu()
    texts = [a.text() for a in window.profile_menu.actions()]
    assert "Main profile" in texts
    assert "Second" in texts
    assert "New profile..." in texts


def test_settings_lists_profiles_with_switch_buttons(qt_app, window,
                                                     isolated_home):
    from PySide6.QtWidgets import QPushButton
    profiles.create("Second")
    window.go("settings")
    pump(qt_app)
    view = window.views["settings"]
    names = [b.text() for b in view.profiles_card.findChildren(QPushButton)]
    assert "Switch" in names
    assert "New profile..." in names
