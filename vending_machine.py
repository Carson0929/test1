#Carson Vanderheyden/100882481
#
import PySimpleGUI as sg
from gpiozero import Button, Servo
from time import sleep
import pytest

class StateMachine:
    # Define SELECTION_LIST as a class attribute
    SELECTION_LIST = [
        ("MARS BAR", "MARS BAR", 2),
        ("KIT KAT", "KIT KAT", 1),
        ("ORANGE CRUSH", "ORANGE CRUSH", 25),
        ("GUMMIE WORMS", "GUMMIE WORMS", 10),
        ("RED BULL", "RED BULL", 5)
    ]

    def __init__(self):
        self.total_amount = 0
        self.current_selection = None
        self.inventory = {item[1]: {"price": item[2], "count": 5} for item in self.SELECTION_LIST}

    def process_coin(self, coin_info, vending_machine):
        coin_value_str = ''.join(filter(str.isdigit, coin_info[0]))

        if coin_value_str:
            coin_value = int(coin_value_str)
            print(f"Coin entered: {coin_value}")
            self.total_amount += coin_value
            self.check_and_dispense(vending_machine)
        else:
            # Handle the "RETURN" button differently
            self.return_coins()

    def make_selection(self, selection):
        print(f"Product selected: {selection}")
        self.current_selection = selection

    def return_coins(self):
        print("Coins returned")
        self.total_amount = 0

    def check_and_dispense(self, vending_machine):
        # Check if the total amount is sufficient for the selected item
        if self.current_selection:
            selected_item = self.inventory.get(self.current_selection)
            if selected_item and self.total_amount >= selected_item["price"] and selected_item["count"] > 0:
                # Dispense the product by moving the servo
                vending_machine.move_servo(1)
                sleep(2)  # Wait for 2 seconds (adjust as needed)
                print(f"Dispensing {self.current_selection}")
                self.return_coins()
                selected_item["count"] -= 1
            else:
                print("Sold out or insufficient funds")
                self.return_coins()
        # Move the servo back to the initial position
        vending_machine.move_servo(0)

class VendingMachine(StateMachine):
    def __init__(self):
        super().__init__()
        # GPIO 5 for the button (adjust the pin number as needed)
        self.button = Button(5)
        # GPIO 17 for the servo (adjust the pin number as needed)
        self.servo = Servo(17, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

    def button_action(self):
        self.return_coins()  # Handle the "RETURN" button differently

    def move_servo(self, position):
        # Move the servo to the specified position (0 for min, 1 for max)
        self.servo.value = position

# PyTest for Challenge 2
@pytest.mark.parametrize("selected_item, expected_inventory", [("MARS BAR", {"MARS BAR": {"price": 2, "count": 4}}),
                                                                ("KIT KAT", {"KIT KAT": {"price": 1, "count": 0}})])
def test_sold_out(selected_item, expected_inventory):
    vending_machine = VendingMachine()
    vending_machine.make_selection(selected_item)
    assert vending_machine.total_amount == 0
    assert vending_machine.inventory == expected_inventory

# PyTest for Challenge 2
@pytest.mark.parametrize("selected_item, expected_inventory", [("MARS BAR", {"MARS BAR": {"price": 2, "count": 0}}),
                                                                ("KIT KAT", {"KIT KAT": {"price": 1, "count": 0}})])
def test_sold_out(selected_item, expected_inventory):
    vending_machine = VendingMachine()
    vending_machine.inventory = {"MARS BAR": {"price": 2, "count": 0}, "KIT KAT": {"price": 1, "count": 0}}
    vending_machine.make_selection(selected_item)
    assert vending_machine.total_amount == 0
    assert vending_machine.inventory == expected_inventory

if __name__ == "__main__":
    vending_machine = VendingMachine()

    # Define the coins and selections
    COIN_LIST = [
        ("2$", "toonie"),
        ("1$", "loonie"),
        ("25¢", "quarter"),
        ("10¢", "dime"),
        ("5¢", "nickel"),
        ("RETURN", "Return")
    ]

    # Define the coins column
    coin_col = [[sg.Text("ENTER COINS")]]
    for item in COIN_LIST:
        button = sg.Button(item[0], key=f"COIN_{item[1]}")  # Unique key for coins
        coin_col.append([button])

    # Define the selections column
    select_col = [[sg.Text("SELECT ITEM")]]
    for item in vending_machine.SELECTION_LIST:
        button_key = f"SELECT_{item[1]}"
        button_disabled = vending_machine.inventory[item[1]]["count"] == 0
        button_color = ("gray", "red") if button_disabled else ("white", "green")
        button = sg.Button(item[0], key=button_key, button_color=button_color, disabled=button_disabled)
        select_col.append([button])

    # Define the layout as two columns separated by a vertical line
    layout = [
        [sg.Column(coin_col, vertical_alignment="TOP"), sg.VSeparator(), sg.Column(select_col, vertical_alignment="TOP")],
        [sg.Text("Amount Entered: "), sg.Text("0", key="-AMOUNT-")],  # Add a Text element for displaying the amount entered
        [sg.Text("Response: "), sg.Output(size=(60, 5), key="-RESPONSE-")]  # Add an Output element for displaying responses
    ]

    # Create the window
    window = sg.Window("Vending Machine", layout)

    # Set up the hardware button callback
    vending_machine.button.when_pressed = vending_machine.button_action

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            print("Shutting down...")
            break
        elif event.startswith("COIN_"):
            coin_pressed = next((item for item in COIN_LIST if f"COIN_{item[1]}" == event), None)
            if coin_pressed is not None:
                vending_machine.process_coin(coin_pressed, vending_machine)
                window["-AMOUNT-"].update(value=f"{vending_machine.total_amount}")
        elif event.startswith("SELECT_"):
            item_selected = event[7:]
            vending_machine.make_selection(item_selected)
        elif event == "RETURN":
            vending_machine.button_action()

        # Update the GUI with responses
        window["-RESPONSE-"].update(value=f"Last Event: {event}, Total Amount: {vending_machine.total_amount}")

    window.close()