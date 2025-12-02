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
    DataTable, Label, Select, RadioSet, RadioButton
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

                # Name editor section (hidden by default)
                with Container(id="name-editor"):
                    yield Label("Patch Name:", classes="detail-label")
                    with Horizontal(id="name-controls"):
                        yield Input(placeholder="Enter patch name...", id="name-input", disabled=True)
                        yield Button("Save", variant="success", id="save-name-btn", disabled=True)

                # Detail scroll container - content added dynamically
                yield VerticalScroll(Static("Select a patch from the list to view details"), id="detail-scroll")

        yield Footer()

    def on_mount(self) -> None:
        """Load patch list when screen mounts"""
        self.load_patches()

    def load_patches(self) -> None:
        """Load all patches (0-99) into the table"""
        table = self.query_one("#patch-table", DataTable)
        table.clear()

        for i in range(100):
            try:
                m = Memory(i)
                name = m.name if m.name else "[empty]"
                table.add_row(f"{i:02d}", name)
            except Exception as e:
                table.add_row(f"{i:02d}", f"[red]Error[/]")

    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in patch table"""
        row_key = event.row_key
        table = self.query_one("#patch-table", DataTable)
        row = table.get_row(row_key)
        slot = int(row[0])

        self.show_patch_details(slot)

    def show_patch_details(self, slot: int) -> None:
        """Display details for selected patch"""
        name_input = self.query_one("#name-input", Input)
        save_btn = self.query_one("#save-name-btn", Button)

        try:
            m = Memory(slot)
            self.selected_memory = m

            # Enable name editor
            name_input.disabled = False
            name_input.value = m.name
            save_btn.disabled = False

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

            # Create tracks table
            tracks_table = DataTable(zebra_stripes=True)
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
                    "✓" if input_setup['rythm'] == '1' else "✗"
                )

            detail_scroll.mount(tracks_table)

        except Exception as e:
            detail_scroll = self.query_one("#detail-scroll", VerticalScroll)
            detail_scroll.remove_children()
            error_msg = Static(f"[red]Error loading patch {slot:02d}:[/red]\n{str(e)}")
            detail_scroll.mount(error_msg)

            # Disable name editor on error
            name_input.disabled = True
            name_input.value = ""
            save_btn.disabled = True

    @on(Button.Pressed, "#save-name-btn")
    def handle_save_name(self) -> None:
        """Save the updated patch name"""
        if not self.selected_memory:
            return

        name_input = self.query_one("#name-input", Input)
        new_name = name_input.value.strip()

        if not new_name:
            self.notify("Name cannot be empty!", severity="error")
            return

        try:
            # Update the name
            self.selected_memory.name = new_name
            self.selected_memory.save()

            # Refresh the patch list and detail view
            self.load_patches()
            self.show_patch_details(self.selected_memory.slot)

            self.notify(f"Saved patch name: {new_name}", severity="information")
        except Exception as e:
            self.notify(f"Error saving patch name: {e}", severity="error")

    def action_refresh_patches(self) -> None:
        """Refresh the patch list"""
        self.notify("Refreshing patch list...", severity="information")
        self.load_patches()
        if self.selected_memory:
            self.show_patch_details(self.selected_memory.slot)
        self.notify("Patch list refreshed!", severity="information")

    def action_update_names(self) -> None:
        """Show update names screen"""
        def on_screen_exit(result=None):
            self.load_patches()
            if self.selected_memory:
                self.show_patch_details(self.selected_memory.slot)

        self.app.push_screen(UpdateNamesScreen(), on_screen_exit)

    def action_config_inputs(self) -> None:
        """Configure track inputs"""
        try:
            update_inputs()
            self.load_patches()
            if self.selected_memory:
                self.show_patch_details(self.selected_memory.slot)
            self.notify("Track inputs configured successfully!", severity="information")
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")

    def action_create_setlist(self) -> None:
        """Show create setlist screen"""
        def on_screen_exit(result=None):
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
                self.load_patches()
                self.query_one("#detail-content", Static).update("Select a patch from the list to view details")
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
