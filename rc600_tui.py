#!/usr/bin/env python3
"""
RC-600 Patch Manager TUI
Modern terminal interface for managing Roland RC-600 patches
"""

import os
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Header, Footer, Button, Static, Input,
    DataTable, Label, Select, RadioSet, RadioButton,
    Switch
)
from textual.screen import Screen, ModalScreen
from textual.binding import Binding

from rc600_patch_manager import Memory, update_names, update_inputs, list_memories


class PathSelectionScreen(ModalScreen[str]):
    """Modal screen for selecting DATA path"""

    CSS = """
    PathSelectionScreen {
        align: center middle;
    }

    #path-dialog {
        width: 70;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }

    #path-title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .path-option {
        margin: 1 0;
    }

    #custom-path-input {
        margin: 1 0;
    }

    #path-buttons {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.default_paths = [
            '/Volumes/RC-600/ROLAND/DATA',
            './DATA'
        ]

    def compose(self) -> ComposeResult:
        with Container(id="path-dialog"):
            yield Label("Select DATA Path", id="path-title")

            with RadioSet(id="path-radio"):
                for i, path in enumerate(self.default_paths):
                    exists = os.path.exists(path)
                    status = "[green]EXISTS[/]" if exists else "[dim]not found[/]"
                    yield RadioButton(f"{path} {status}", value=path, id=f"path-{i}")
                yield RadioButton("Custom path", value="custom", id="path-custom")

            yield Input(
                placeholder="Enter custom path...",
                id="custom-path-input",
                disabled=True
            )

            with Horizontal(id="path-buttons"):
                yield Button("OK", variant="primary", id="path-ok")
                yield Button("Cancel", variant="default", id="path-cancel")

    @on(RadioSet.Changed)
    def radio_changed(self, event: RadioSet.Changed) -> None:
        """Enable custom input when custom is selected"""
        custom_input = self.query_one("#custom-path-input", Input)
        custom_input.disabled = event.pressed.id != "path-custom"
        if not custom_input.disabled:
            custom_input.focus()

    @on(Button.Pressed, "#path-ok")
    def handle_ok(self) -> None:
        """Handle OK button press"""
        radio_set = self.query_one("#path-radio", RadioSet)

        if radio_set.pressed_button and radio_set.pressed_button.id == "path-custom":
            custom_input = self.query_one("#custom-path-input", Input)
            path = custom_input.value.strip()
            if path:
                self.dismiss(path)
            else:
                return
        elif radio_set.pressed_button:
            # Get the index from the button ID to retrieve the actual path
            button_id = radio_set.pressed_button.id
            if button_id.startswith("path-") and button_id != "path-custom":
                index = int(button_id.split("-")[1])
                self.dismiss(self.default_paths[index])
            else:
                return

    @on(Button.Pressed, "#path-cancel")
    def handle_cancel(self) -> None:
        """Handle cancel button press"""
        self.dismiss(None)


class UpdateNamesScreen(Screen):
    """Screen for updating patch names from CSV"""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
    ]

    CSS = """
    UpdateNamesScreen {
        align: center middle;
    }

    #update-container {
        width: 80;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    .form-field {
        margin: 1 0;
    }

    #update-buttons {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="update-container"):
            yield Label("Update Patch Names from CSV", classes="form-field")
            yield Input(
                placeholder="./lista.csv",
                value="./lista.csv",
                id="csv-filename"
            )
            yield Label("", id="status-message", classes="form-field")

            with Horizontal(id="update-buttons"):
                yield Button("Update", variant="primary", id="update-btn")
                yield Button("Back", variant="default", id="back-btn")
        yield Footer()

    @on(Button.Pressed, "#update-btn")
    def handle_update(self) -> None:
        """Handle update button"""
        csv_input = self.query_one("#csv-filename", Input)
        status = self.query_one("#status-message", Label)

        try:
            update_names(csv_input.value)
            status.update("[green]✓ Patch names updated successfully![/]")
        except Exception as e:
            status.update(f"[red]✗ Error: {e}[/]")

    @on(Button.Pressed, "#back-btn")
    def handle_back(self) -> None:
        """Go back to main screen"""
        self.app.pop_screen()


class CreateSetlistScreen(Screen):
    """Screen for creating setlist from CSV"""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
    ]

    CSS = """
    CreateSetlistScreen {
        align: center middle;
    }

    #setlist-container {
        width: 80;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    .form-field {
        margin: 1 0;
    }

    #setlist-buttons {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="setlist-container"):
            yield Label("Create Setlist from CSV", classes="form-field")
            yield Input(
                placeholder="./2025-11-13-Recital.csv",
                value="./2025-11-13-Recital.csv",
                id="setlist-filename"
            )
            yield Label("", id="status-message", classes="form-field")

            with Horizontal(id="setlist-buttons"):
                yield Button("Create", variant="primary", id="create-btn")
                yield Button("Back", variant="default", id="back-btn")
        yield Footer()

    @on(Button.Pressed, "#create-btn")
    def handle_create(self) -> None:
        """Handle create button"""
        csv_input = self.query_one("#setlist-filename", Input)
        status = self.query_one("#status-message", Label)

        try:
            import csv
            with open(csv_input.value, 'r') as f:
                reader = csv.DictReader(f)
                slot = 1
                for row in reader:
                    mem = Memory(int(row['Banco']))
                    mem.name = row['ShortName']
                    mem.save(slot=slot)
                    slot += 1
            status.update(f"[green]✓ Setlist created successfully! ({slot-1} patches)[/]")
        except Exception as e:
            status.update(f"[red]✗ Error: {e}[/]")

    @on(Button.Pressed, "#back-btn")
    def handle_back(self) -> None:
        """Go back to main screen"""
        self.app.pop_screen()


class CopyPatchScreen(Screen):
    """Screen for copying patch settings to other patches"""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
    ]

    CSS = """
    CopyPatchScreen {
    }

    #copy-container {
        layout: vertical;
        width: 100%;
        height: 100%;
        background: $surface;
        padding: 1 2;
    }

    #copy-title {
        width: 100%;
        text-style: bold;
        color: $accent;
        height: auto;
    }

    #copy-options {
        width: 100%;
        height: auto;
        padding: 1;
        border: solid $primary;
    }

    #copy-options Label {
        height: auto;
    }

    #copy-options Horizontal {
        height: auto;
        margin: 0;
    }

    #copy-options Button {
        min-width: 15;
    }

    #target-section-label {
        width: 100%;
        height: auto;
        margin-top: 1;
    }

    #target-list-container {
        width: 100%;
        height: 1fr;
        border: solid $primary;
    }

    #target-table {
        width: 100%;
        height: 100%;
    }

    #copy-buttons {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 1;
    }

    .option-label {
        margin: 0 1 0 0;
        width: auto;
    }
    """

    def __init__(self, source_slot: int, source_name: str):
        super().__init__()
        self.source_slot = source_slot
        self.source_name = source_name
        self.selected_targets = set()

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="copy-container"):
            yield Label(f"Copy from Slot {self.source_slot:02d}: {self.source_name}", id="copy-title")

            # Copy options
            with Container(id="copy-options"):
                yield Label("[bold]Copy Options:[/bold]")
                with Horizontal():
                    yield Label("Effects (IFX/TFX):", classes="option-label")
                    yield Button("Copy Effects", id="copy-effects-toggle", variant="default")
                with Horizontal():
                    yield Label("Assigns:", classes="option-label")
                    yield Button("All (1-16)", id="copy-assigns-all-toggle", variant="default")
                    yield Button("1-8", id="copy-assigns-1-8-toggle", variant="default")
                    yield Button("9-16", id="copy-assigns-9-16-toggle", variant="default")

            # Target selection
            yield Label("[bold]Select Target Patches:[/bold]", id="target-section-label")
            with Container(id="target-list-container"):
                table = DataTable(id="target-table", zebra_stripes=True, cursor_type="row")
                table.add_columns("Select", "Slot", "Name")
                yield table

            with Horizontal(id="copy-buttons"):
                yield Button("Copy to Selected", variant="primary", id="copy-btn")
                yield Button("Select All", variant="default", id="select-all-btn")
                yield Button("Deselect All", variant="default", id="deselect-all-btn")
                yield Button("Back", variant="default", id="back-btn")
        yield Footer()

    def on_mount(self) -> None:
        """Load target list when screen mounts"""
        self.copy_effects = False
        self.copy_assigns = set()
        self.load_targets()

    def load_targets(self) -> None:
        """Load all patches except source into target table"""
        table = self.query_one("#target-table", DataTable)
        table.clear()

        for i in range(100):
            if i == self.source_slot:
                continue
            try:
                m = Memory(i)
                name = m.name if m.name else "[empty]"
                selected = "✓" if i in self.selected_targets else " "
                table.add_row(selected, f"{i:02d}", name, key=str(i))
            except Exception as e:
                table.add_row(" ", f"{i:02d}", f"[red]Error[/]", key=str(i))

    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        """Toggle target selection"""
        table = self.query_one("#target-table", DataTable)
        slot = int(event.row_key.value)

        # Toggle selection
        if slot in self.selected_targets:
            self.selected_targets.remove(slot)
        else:
            self.selected_targets.add(slot)

        # Update only this row instead of reloading all patches
        # Get the column key for the "Select" column (first column, index 0)
        select_column = table.ordered_columns[0]
        selected = "✓" if slot in self.selected_targets else " "
        table.update_cell(event.row_key, select_column.key, selected)

    @on(Button.Pressed, "#copy-effects-toggle")
    def toggle_copy_effects(self) -> None:
        """Toggle copy effects option"""
        self.copy_effects = not self.copy_effects
        btn = self.query_one("#copy-effects-toggle", Button)
        btn.variant = "success" if self.copy_effects else "default"

    @on(Button.Pressed, "#copy-assigns-all-toggle")
    def toggle_copy_assigns_all(self) -> None:
        """Toggle all assigns"""
        if len(self.copy_assigns) == 16:
            self.copy_assigns.clear()
            self.query_one("#copy-assigns-all-toggle", Button).variant = "default"
            self.query_one("#copy-assigns-1-8-toggle", Button).variant = "default"
            self.query_one("#copy-assigns-9-16-toggle", Button).variant = "default"
        else:
            self.copy_assigns = set(range(1, 17))
            self.query_one("#copy-assigns-all-toggle", Button).variant = "success"
            self.query_one("#copy-assigns-1-8-toggle", Button).variant = "success"
            self.query_one("#copy-assigns-9-16-toggle", Button).variant = "success"

    @on(Button.Pressed, "#copy-assigns-1-8-toggle")
    def toggle_copy_assigns_1_8(self) -> None:
        """Toggle assigns 1-8"""
        assigns_1_8 = set(range(1, 9))
        if assigns_1_8.issubset(self.copy_assigns):
            self.copy_assigns -= assigns_1_8
            self.query_one("#copy-assigns-1-8-toggle", Button).variant = "default"
        else:
            self.copy_assigns |= assigns_1_8
            self.query_one("#copy-assigns-1-8-toggle", Button).variant = "success"

        # Update All button
        if len(self.copy_assigns) == 16:
            self.query_one("#copy-assigns-all-toggle", Button).variant = "success"
        else:
            self.query_one("#copy-assigns-all-toggle", Button).variant = "default"

    @on(Button.Pressed, "#copy-assigns-9-16-toggle")
    def toggle_copy_assigns_9_16(self) -> None:
        """Toggle assigns 9-16"""
        assigns_9_16 = set(range(9, 17))
        if assigns_9_16.issubset(self.copy_assigns):
            self.copy_assigns -= assigns_9_16
            self.query_one("#copy-assigns-9-16-toggle", Button).variant = "default"
        else:
            self.copy_assigns |= assigns_9_16
            self.query_one("#copy-assigns-9-16-toggle", Button).variant = "success"

        # Update All button
        if len(self.copy_assigns) == 16:
            self.query_one("#copy-assigns-all-toggle", Button).variant = "success"
        else:
            self.query_one("#copy-assigns-all-toggle", Button).variant = "default"

    @on(Button.Pressed, "#select-all-btn")
    def select_all_targets(self) -> None:
        """Select all targets"""
        self.selected_targets = set(range(100)) - {self.source_slot}
        self.load_targets()

    @on(Button.Pressed, "#deselect-all-btn")
    def deselect_all_targets(self) -> None:
        """Deselect all targets"""
        self.selected_targets.clear()
        self.load_targets()

    @on(Button.Pressed, "#copy-btn")
    def handle_copy(self) -> None:
        """Stage the copy operation"""
        if not self.selected_targets:
            self.notify("No targets selected!", severity="error")
            return

        if not self.copy_effects and not self.copy_assigns:
            self.notify("No copy options selected!", severity="error")
            return

        # Create copy operation data
        copy_operation = {
            'source': self.source_slot,
            'targets': list(self.selected_targets),
            'copy_effects': self.copy_effects,
            'copy_assigns': list(self.copy_assigns)
        }

        # Return the operation to be staged
        self.dismiss(copy_operation)

    @on(Button.Pressed, "#back-btn")
    def handle_back(self) -> None:
        """Go back to main screen"""
        self.dismiss(None)


class ListMemoriesScreen(Screen):
    """Screen for listing memory slots"""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "refresh", "Refresh"),
    ]

    CSS = """
    ListMemoriesScreen {
        align: center middle;
    }

    #list-container {
        width: 90;
        height: 40;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    #memory-table {
        height: 1fr;
        margin: 1 0;
    }

    #list-buttons {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    """

    def __init__(self, start: int = 30, end: int = 40):
        super().__init__()
        self.start = start
        self.end = end

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="list-container"):
            yield Label(f"Memory Slots ({self.start}-{self.end-1})")

            table = DataTable(id="memory-table")
            table.add_columns("Slot", "Bank", "Count", "Name")
            yield table

            with Horizontal(id="list-buttons"):
                yield Button("Refresh", variant="primary", id="refresh-btn")
                yield Button("Back", variant="default", id="back-btn")
        yield Footer()

    def on_mount(self) -> None:
        """Load data when screen mounts"""
        self.load_memories()

    def load_memories(self) -> None:
        """Load memory slots into table"""
        table = self.query_one("#memory-table", DataTable)
        table.clear()

        for i in range(self.start, self.end):
            try:
                m = Memory(i)
                table.add_row(
                    str(i),
                    m.seq,
                    f"{m.count:04X}",
                    m.name
                )
            except Exception as e:
                table.add_row(
                    str(i),
                    "-",
                    "-",
                    f"[red]Error: {str(e)[:30]}[/]"
                )

    @on(Button.Pressed, "#refresh-btn")
    def action_refresh(self) -> None:
        """Refresh the memory list"""
        self.load_memories()

    @on(Button.Pressed, "#back-btn")
    def handle_back(self) -> None:
        """Go back to main screen"""
        self.app.pop_screen()


class TrackSettingsScreen(Screen):
    """Screen for editing track settings"""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
    ]

    CSS = """
    TrackSettingsScreen {
        layout: vertical;
    }

    #track-settings-container {
        width: 100%;
        height: 100%;
        layout: vertical;
        padding: 1 2;
    }

    #track-settings-title {
        width: 100%;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    #track-settings-scroll {
        width: 100%;
        height: 1fr;
        border: solid $primary;
    }

    .settings-section {
        width: 100%;
        margin: 1 0;
        padding: 1;
        border: solid $primary-darken-2;
    }

    .section-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .setting-row {
        height: auto;
        width: 100%;
        align: left middle;
        margin: 0 0 1 0;
    }

    .setting-label {
        width: 20;
    }

    .setting-value {
        width: 10;
        color: $text-muted;
    }

    #track-settings-buttons {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    """

    def __init__(self, patch_slot: int, track_num: int, track, on_stage_callback):
        super().__init__()
        self.patch_slot = patch_slot
        self.track_num = track_num
        self.track = track
        self.on_stage_callback = on_stage_callback
        self.pending_changes = {}

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="track-settings-container"):
            yield Label(f"Track {self.track_num} Settings - Patch {self.patch_slot:02d}", id="track-settings-title")

            with VerticalScroll(id="track-settings-scroll"):
                # Playback Settings Section
                with Container(classes="settings-section"):
                    yield Label("[bold]Playback Settings[/bold]", classes="section-title")

                    with Horizontal(classes="setting-row"):
                        yield Label("Reverse:", classes="setting-label")
                        yield Switch(value=bool(self.track.reverse), id="reverse")
                        yield Label(f"({self.track.reverse})", classes="setting-value")

                    with Horizontal(classes="setting-row"):
                        yield Label("One Shot:", classes="setting-label")
                        yield Switch(value=bool(self.track.one_shot), id="one_shot")
                        yield Label(f"({self.track.one_shot})", classes="setting-value")

                    with Horizontal(classes="setting-row"):
                        yield Label("Playback FX:", classes="setting-label")
                        yield Switch(value=bool(self.track.playback_fx), id="playback_fx")
                        yield Label(f"({self.track.playback_fx})", classes="setting-value")

                    with Horizontal(classes="setting-row"):
                        yield Label("Balance:", classes="setting-label")
                        yield Label(str(self.track.balance), id="balance-display", classes="setting-value")

                    with Horizontal(classes="setting-row"):
                        yield Label("Play Level:", classes="setting-label")
                        yield Label(str(self.track.play_level), id="level-display", classes="setting-value")

                # Track Type and Modes Section
                with Container(classes="settings-section"):
                    yield Label("[bold]Track Type & Modes[/bold]", classes="section-title")

                    with Horizontal(classes="setting-row"):
                        yield Label("Track Type:", classes="setting-label")
                        yield Switch(value=bool(self.track.track_type), id="track_type")
                        yield Label(f"({'Single' if self.track.track_type else 'Multi'})", classes="setting-value")

                    with Horizontal(classes="setting-row"):
                        yield Label("Tempo Sync:", classes="setting-label")
                        yield Switch(value=bool(self.track.tempo_sync), id="tempo_sync")
                        yield Label(f"({self.track.tempo_sync})", classes="setting-value")

                    with Horizontal(classes="setting-row"):
                        yield Label("Playback Mode:", classes="setting-label")
                        yield Label(str(self.track.playback_mode), id="playback-mode-display", classes="setting-value")

                    with Horizontal(classes="setting-row"):
                        yield Label("Start Trigger:", classes="setting-label")
                        yield Label(str(self.track.start_trigger_mode), id="start-trigger-display", classes="setting-value")

                    with Horizontal(classes="setting-row"):
                        yield Label("Stop Mode:", classes="setting-label")
                        yield Label(str(self.track.stop_mode), id="stop-mode-display", classes="setting-value")

                    with Horizontal(classes="setting-row"):
                        yield Label("Overdub Mode:", classes="setting-label")
                        yield Label(str(self.track.overdub_mode), id="overdub-mode-display", classes="setting-value")

                # FX Assignments Section
                with Container(classes="settings-section"):
                    yield Label("[bold]FX Assignments[/bold]", classes="section-title")

                    with Horizontal(classes="setting-row"):
                        yield Label("FX1 Assign:", classes="setting-label")
                        yield Switch(value=bool(self.track.fx1_assign), id="fx1_assign")
                        yield Label(f"({self.track.fx1_assign})", classes="setting-value")

                    with Horizontal(classes="setting-row"):
                        yield Label("FX2 Assign:", classes="setting-label")
                        yield Switch(value=bool(self.track.fx2_assign), id="fx2_assign")
                        yield Label(f"({self.track.fx2_assign})", classes="setting-value")

                    with Horizontal(classes="setting-row"):
                        yield Label("FX3 Assign:", classes="setting-label")
                        yield Switch(value=bool(self.track.fx3_assign), id="fx3_assign")
                        yield Label(f"({self.track.fx3_assign})", classes="setting-value")

                # Timing Settings Section
                with Container(classes="settings-section"):
                    yield Label("[bold]Timing Settings[/bold]", classes="section-title")

                    with Horizontal(classes="setting-row"):
                        yield Label("Rhythm Sync:", classes="setting-label")
                        yield Switch(value=bool(self.track.rhythm_sync), id="rhythm_sync")
                        yield Label(f"({self.track.rhythm_sync})", classes="setting-value")

                    with Horizontal(classes="setting-row"):
                        yield Label("Quantize:", classes="setting-label")
                        yield Switch(value=bool(self.track.quantize), id="quantize")
                        yield Label(f"({self.track.quantize})", classes="setting-value")

            with Horizontal(id="track-settings-buttons"):
                yield Button("Stage Changes", variant="primary", id="stage-btn")
                yield Button("Back", variant="default", id="back-btn")
        yield Footer()

    @on(Switch.Changed)
    def handle_switch_change(self, event: Switch.Changed) -> None:
        """Track switch changes"""
        switch_id = event.switch.id
        value = 1 if event.value else 0
        self.pending_changes[switch_id] = value

    @on(Button.Pressed, "#stage-btn")
    def handle_stage(self) -> None:
        """Stage the track setting changes"""
        if not self.pending_changes:
            self.notify("No changes made", severity="warning")
            return

        # Create settings change data
        settings_data = {
            'patch_slot': self.patch_slot,
            'track_num': self.track_num,
            'changes': self.pending_changes.copy()
        }

        # Call the callback to stage changes
        self.on_stage_callback(settings_data)

        changes_count = len(self.pending_changes)
        self.notify(f"Staged {changes_count} track setting{'s' if changes_count != 1 else ''}", severity="information")
        self.dismiss(True)

    @on(Button.Pressed, "#back-btn")
    def handle_back(self) -> None:
        """Go back without staging"""
        self.dismiss(False)


class MainScreen(Screen):
    """Main screen with patch list and details"""

    BINDINGS = [
        Binding("r", "refresh_patches", "Refresh", show=True),
        Binding("u", "update_names", "Update Names", show=True),
        Binding("i", "config_inputs", "Config Inputs", show=True),
        Binding("s", "create_setlist", "Setlist", show=True),
        Binding("p", "change_path", "Change Path", show=True),
    ]

    CSS = """
    MainScreen {
        layout: horizontal;
    }

    #left-panel {
        width: 35;
        height: 100%;
        border-right: solid $primary;
        background: $surface;
    }

    #patch-list-container {
        width: 100%;
        height: 100%;
        padding: 1;
    }

    #patch-list-title {
        width: 100%;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    #patch-table {
        height: 1fr;
    }

    #right-panel {
        width: 1fr;
        height: 100%;
        background: $surface;
    }

    #detail-container {
        width: 100%;
        height: 100%;
        padding: 2;
    }

    #detail-title {
        width: 100%;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    #name-editor {
        width: 100%;
        height: auto;
        margin-bottom: 1;
        padding: 1;
        border: solid $primary;
        background: $surface;
    }

    #name-input {
        width: 1fr;
        margin: 0 1;
    }

    #name-controls {
        width: 100%;
        height: auto;
        align: left middle;
    }

    #save-name-btn {
        margin-left: 1;
    }

    #apply-changes-container {
        width: 100%;
        height: auto;
        padding: 1;
        background: $surface;
        border: solid $accent;
        margin-bottom: 1;
    }

    #apply-changes-label {
        text-style: bold;
        color: $accent;
    }

    #detail-scroll {
        width: 100%;
        height: 1fr;
        border: solid $primary;
        padding: 1;
    }

    #detail-scroll > Static {
        margin-bottom: 1;
    }

    #detail-scroll > DataTable {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, data_path: str):
        super().__init__()
        self.data_path = data_path
        self.selected_memory = None

        # Caching and modification tracking
        self.patch_cache = {}  # slot -> Memory object
        self.modified_patches = set()  # Set of modified slot numbers
        self.pending_name_changes = {}  # slot -> new_name
        self.pending_copy_operations = []  # List of copy operations to apply
        self.pending_track_settings = []  # List of track setting changes

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        # Left panel with patch list
        with Container(id="left-panel"):
            with VerticalScroll(id="patch-list-container"):
                yield Label("Patches (0-99)", id="patch-list-title")
                table = DataTable(id="patch-table", zebra_stripes=True, cursor_type="row")
                table.add_columns("Slot", "Name")
                yield table

        # Right panel with patch details
        with Container(id="right-panel"):
            with Container(id="detail-container"):
                yield Label("Patch Details", id="detail-title")

                # Apply changes section
                with Horizontal(id="apply-changes-container"):
                    yield Label("Pending changes: 0", id="apply-changes-label")
                    yield Button("Apply All Changes", variant="primary", id="apply-all-btn", disabled=True)

                # Name editor section (hidden by default)
                with Container(id="name-editor"):
                    yield Label("Patch Name:", classes="detail-label")
                    with Horizontal(id="name-controls"):
                        yield Input(placeholder="Enter patch name...", id="name-input", disabled=True)
                        yield Button("Save", variant="success", id="save-name-btn", disabled=True)
                        yield Button("Copy Settings...", variant="warning", id="copy-settings-btn", disabled=True)

                # Detail scroll container - content added dynamically
                yield VerticalScroll(Static("Select a patch from the list to view details"), id="detail-scroll")

        yield Footer()

    def on_mount(self) -> None:
        """Load patch list when screen mounts"""
        self.load_patches()

    def load_patches(self) -> None:
        """Load all patches (0-99) into the table with caching"""
        table = self.query_one("#patch-table", DataTable)
        table.clear()

        for i in range(100):
            try:
                # Use cache if available, otherwise load and cache
                if i not in self.patch_cache:
                    self.patch_cache[i] = Memory(i)

                m = self.patch_cache[i]

                # Determine name to display (pending change or current)
                if i in self.pending_name_changes:
                    name = self.pending_name_changes[i]
                else:
                    name = m.name if m.name else "[empty]"

                # Add modified indicator
                if i in self.modified_patches:
                    name = f"• {name}"

                table.add_row(f"{i:02d}", name)
            except Exception as e:
                table.add_row(f"{i:02d}", f"[red]Error[/]")

    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in patch table or tracks table"""
        # Check which table was clicked
        if event.data_table.id == "patch-table":
            # Patch table - show patch details
            row_key = event.row_key
            table = self.query_one("#patch-table", DataTable)
            row = table.get_row(row_key)
            slot = int(row[0])
            self.show_patch_details(slot)

        elif event.data_table.id == "tracks-detail-table":
            # Tracks table - open track settings
            if not self.selected_memory:
                return

            track_num = int(event.row_key.value)
            track = self.selected_memory.tracks[track_num - 1]

            def on_stage_track_settings(settings_data):
                """Callback when track settings are staged"""
                self.pending_track_settings.append(settings_data)
                self.modified_patches.add(settings_data['patch_slot'])
                self.update_pending_changes_ui()
                self.load_patches()

            self.app.push_screen(
                TrackSettingsScreen(
                    self.selected_memory.slot,
                    track_num,
                    track,
                    on_stage_track_settings
                )
            )

    def show_patch_details(self, slot: int) -> None:
        """Display details for selected patch"""
        name_input = self.query_one("#name-input", Input)
        save_btn = self.query_one("#save-name-btn", Button)
        copy_btn = self.query_one("#copy-settings-btn", Button)

        try:
            # Use cached memory or load if not cached
            if slot not in self.patch_cache:
                self.patch_cache[slot] = Memory(slot)

            m = self.patch_cache[slot]
            self.selected_memory = m

            # Enable name editor and copy button
            name_input.disabled = False
            # Show pending name change if exists, otherwise current name
            if slot in self.pending_name_changes:
                name_input.value = self.pending_name_changes[slot]
            else:
                name_input.value = m.name
            save_btn.disabled = False
            copy_btn.disabled = False

            # Clear and rebuild the detail scroll container
            detail_scroll = self.query_one("#detail-scroll", VerticalScroll)
            detail_scroll.remove_children()

            # Add basic info
            info = Static()
            info_text = f"[bold cyan]Memory Slot {slot:02d}[/bold cyan]\n\n"
            info_text += f"[bold]Bank:[/bold] {m.seq}\n"
            info_text += f"[bold]Count:[/bold] {m.count:04X}\n"

            # Add BPM if available
            if m.bpm is not None:
                info_text += f"[bold]BPM:[/bold] {m.bpm:.1f}\n"

            info_text += f"[bold]File:[/bold] {m.xml_path}\n\n"
            info_text += f"[bold yellow]Track Input Configuration:[/bold yellow]\n"
            info.update(info_text)
            detail_scroll.mount(info)

            # Create tracks table (clickable to edit settings)
            tracks_table = DataTable(zebra_stripes=True, cursor_type="row", id="tracks-detail-table")
            tracks_table.add_columns("Track", "Mic1", "Mic2", "Inst1L", "Inst1R", "Inst2L", "Inst2R", "Rhythm")

            for i, track in enumerate(m.tracks, 1):
                input_setup = track.input_setup
                tracks_table.add_row(
                    f"Track {i}",
                    "✓" if input_setup['mic1'] == '1' else "✗",
                    "✓" if input_setup['mic2'] == '1' else "✗",
                    "✓" if input_setup['inst1l'] == '1' else "✗",
                    "✓" if input_setup['inst1r'] == '1' else "✗",
                    "✓" if input_setup['inst2l'] == '1' else "✗",
                    "✓" if input_setup['inst2r'] == '1' else "✗",
                    "✓" if input_setup['rythm'] == '1' else "✗",
                    key=str(i)
                )

            detail_scroll.mount(tracks_table)

        except Exception as e:
            detail_scroll = self.query_one("#detail-scroll", VerticalScroll)
            detail_scroll.remove_children()
            error_msg = Static(f"[red]Error loading patch {slot:02d}:[/red]\n{str(e)}")
            detail_scroll.mount(error_msg)

            # Disable name editor and copy button on error
            name_input.disabled = True
            name_input.value = ""
            save_btn.disabled = True
            copy_btn.disabled = True

    @on(Button.Pressed, "#save-name-btn")
    def handle_save_name(self) -> None:
        """Add patch name change to pending changes"""
        if not self.selected_memory:
            return

        name_input = self.query_one("#name-input", Input)
        new_name = name_input.value.strip()

        if not new_name:
            self.notify("Name cannot be empty!", severity="error")
            return

        slot = self.selected_memory.slot

        # Add to pending changes
        self.pending_name_changes[slot] = new_name
        self.modified_patches.add(slot)

        # Update UI
        self.update_pending_changes_ui()
        self.load_patches()

        self.notify(f"Name change staged for slot {slot:02d}", severity="information")

    def update_pending_changes_ui(self) -> None:
        """Update the pending changes counter and button state"""
        # Count name changes, copy operations, and track settings
        name_changes = len(self.pending_name_changes)
        copy_ops = len(self.pending_copy_operations)
        track_settings = len(self.pending_track_settings)
        total_count = len(self.modified_patches)

        label = self.query_one("#apply-changes-label", Label)
        button = self.query_one("#apply-all-btn", Button)

        # Build detailed message
        parts = []
        if name_changes > 0:
            parts.append(f"{name_changes} name{'s' if name_changes != 1 else ''}")
        if copy_ops > 0:
            total_targets = sum(len(op['targets']) for op in self.pending_copy_operations)
            parts.append(f"{copy_ops} copy op{'s' if copy_ops != 1 else ''} ({total_targets} targets)")
        if track_settings > 0:
            parts.append(f"{track_settings} track setting{'s' if track_settings != 1 else ''}")

        if parts:
            msg = f"Pending: {', '.join(parts)}"
        else:
            msg = "No pending changes"

        label.update(msg)
        button.disabled = total_count == 0

    @on(Button.Pressed, "#apply-all-btn")
    def handle_apply_changes(self) -> None:
        """Apply all pending changes to disk"""
        if not self.modified_patches:
            return

        try:
            saved_count = 0
            errors = []

            # Apply name changes
            for slot in list(self.pending_name_changes.keys()):
                try:
                    if slot in self.patch_cache:
                        m = self.patch_cache[slot]
                        m.name = self.pending_name_changes[slot]
                        m.save()
                        saved_count += 1
                except Exception as e:
                    errors.append(f"Name change slot {slot:02d}: {e}")

            # Apply copy operations
            copy_count = 0
            for op in self.pending_copy_operations:
                try:
                    source_slot = op['source']
                    targets = op['targets']
                    copy_effects = op['copy_effects']
                    copy_assigns = op['copy_assigns']

                    # Load source if not cached
                    if source_slot not in self.patch_cache:
                        self.patch_cache[source_slot] = Memory(source_slot)
                    source = self.patch_cache[source_slot]

                    # Build node list
                    nodes_to_copy = []
                    for assign_num in copy_assigns:
                        nodes_to_copy.append(f'./mem/ASSIGN{assign_num}')
                    if copy_effects:
                        nodes_to_copy.append('./ifx')
                        nodes_to_copy.append('./tfx')

                    # Copy to each target
                    for target_slot in targets:
                        try:
                            # Load target if not cached
                            if target_slot not in self.patch_cache:
                                self.patch_cache[target_slot] = Memory(target_slot)
                            dest = self.patch_cache[target_slot]

                            for node_path in nodes_to_copy:
                                source.copy_to(dest, node_path)
                            dest.save()
                            copy_count += 1
                        except Exception as e:
                            errors.append(f"Copy to slot {target_slot:02d}: {e}")

                except Exception as e:
                    errors.append(f"Copy operation: {e}")

            # Apply track settings changes
            track_count = 0
            for settings_data in self.pending_track_settings:
                try:
                    patch_slot = settings_data['patch_slot']
                    track_num = settings_data['track_num']
                    changes = settings_data['changes']

                    # Load patch if not cached
                    if patch_slot not in self.patch_cache:
                        self.patch_cache[patch_slot] = Memory(patch_slot)
                    m = self.patch_cache[patch_slot]
                    track = m.tracks[track_num - 1]

                    # Apply each setting change
                    for setting_name, value in changes.items():
                        setattr(track, setting_name, value)

                    m.save()
                    track_count += 1
                except Exception as e:
                    errors.append(f"Track settings patch {patch_slot:02d} track {track_num}: {e}")

            # Clear pending changes
            self.modified_patches.clear()
            self.pending_name_changes.clear()
            self.pending_copy_operations.clear()
            self.pending_track_settings.clear()

            # Clear cache to reload fresh data
            self.patch_cache.clear()

            # Update UI
            self.update_pending_changes_ui()
            self.load_patches()

            if self.selected_memory:
                self.show_patch_details(self.selected_memory.slot)

            # Show result
            total_ops = saved_count + copy_count + track_count
            if errors:
                error_msg = "\n".join(errors[:5])  # Show first 5 errors
                self.notify(f"Applied {total_ops} operations with errors:\n{error_msg}", severity="warning")
            else:
                msg_parts = []
                if saved_count > 0:
                    msg_parts.append(f"{saved_count} name change{'s' if saved_count != 1 else ''}")
                if copy_count > 0:
                    msg_parts.append(f"{copy_count} copy operation{'s' if copy_count != 1 else ''}")
                if track_count > 0:
                    msg_parts.append(f"{track_count} track setting{'s' if track_count != 1 else ''}")
                msg = "Successfully applied " + ", ".join(msg_parts) + "!"
                self.notify(msg, severity="information")

        except Exception as e:
            self.notify(f"Error applying changes: {e}", severity="error")

    @on(Button.Pressed, "#copy-settings-btn")
    def handle_copy_settings(self) -> None:
        """Open copy settings screen"""
        if not self.selected_memory:
            return

        def on_copy_exit(result):
            # Handle copy operation result
            if result:
                # Add to pending copy operations
                self.pending_copy_operations.append(result)

                # Mark all target patches as modified
                for target_slot in result['targets']:
                    self.modified_patches.add(target_slot)

                # Update UI
                self.update_pending_changes_ui()
                self.load_patches()

                target_count = len(result['targets'])
                self.notify(f"Copy operation staged for {target_count} target{'s' if target_count != 1 else ''}", severity="information")

        self.app.push_screen(
            CopyPatchScreen(self.selected_memory.slot, self.selected_memory.name),
            on_copy_exit
        )

    def action_refresh_patches(self) -> None:
        """Refresh the patch list"""
        self.notify("Refreshing patch list...", severity="information")
        # Clear cache to force reload from disk
        self.patch_cache.clear()
        self.load_patches()
        if self.selected_memory:
            self.show_patch_details(self.selected_memory.slot)
        self.notify("Patch list refreshed!", severity="information")

    def action_update_names(self) -> None:
        """Show update names screen"""
        def on_screen_exit(result=None):
            self.patch_cache.clear()
            self.load_patches()
            if self.selected_memory:
                self.show_patch_details(self.selected_memory.slot)

        self.app.push_screen(UpdateNamesScreen(), on_screen_exit)

    def action_config_inputs(self) -> None:
        """Configure track inputs"""
        try:
            update_inputs()
            self.patch_cache.clear()
            self.load_patches()
            if self.selected_memory:
                self.show_patch_details(self.selected_memory.slot)
            self.notify("Track inputs configured successfully!", severity="information")
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")

    def action_create_setlist(self) -> None:
        """Show create setlist screen"""
        def on_screen_exit(result=None):
            self.patch_cache.clear()
            self.load_patches()
            if self.selected_memory:
                self.show_patch_details(self.selected_memory.slot)

        self.app.push_screen(CreateSetlistScreen(), on_screen_exit)

    def action_change_path(self) -> None:
        """Change DATA path"""
        def handle_path_result(path: str | None) -> None:
            if path:
                Memory.cwd = path
                self.data_path = path
                # Clear all caches and pending changes
                self.patch_cache.clear()
                self.modified_patches.clear()
                self.pending_name_changes.clear()
                self.pending_copy_operations.clear()
                self.pending_track_settings.clear()
                self.update_pending_changes_ui()
                self.load_patches()
                self.selected_memory = None
                self.notify(f"Path changed to: {path}", severity="information")

        self.app.push_screen(PathSelectionScreen(), handle_path_result)


class RC600App(App):
    """RC-600 Patch Manager TUI Application"""

    CSS = """
    Screen {
        background: $background;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.data_path = None

    def on_mount(self) -> None:
        """Show path selection on startup"""
        def handle_initial_path(path: str | None) -> None:
            if path:
                self.data_path = path
                Memory.cwd = path
                self.push_screen(MainScreen(path))
            else:
                self.exit()

        self.push_screen(PathSelectionScreen(), handle_initial_path)


def main():
    """Run the TUI application"""
    app = RC600App()
    app.run()


if __name__ == '__main__':
    main()
