import pytest
from your_vending_machine_file import VendingMachine

# Test for Challenge 1
def test_process_coin():
    vending_machine = VendingMachine()

    # Test with valid coins
    vending_machine.process_coin(("2$", "toonie"), vending_machine)
    assert vending_machine.total_amount == 2

    # Test with invalid coins
    vending_machine.process_coin(("Invalid Coin", "invalid_coin"), vending_machine)
    assert vending_machine.total_amount == 2  # Total amount should remain the same for invalid coins

# Test for Challenge 2
@pytest.mark.parametrize("selected_item, expected_inventory", [
    ("MARS BAR", {"MARS BAR": {"price": 2, "count": 4}}),
    ("KIT KAT", {"KIT KAT": {"price": 1, "count": 0}})
])
def test_sold_out(selected_item, expected_inventory):
    vending_machine = VendingMachine()
    vending_machine.make_selection(selected_item)
    assert vending_machine.total_amount == 0
    assert vending_machine.inventory == expected_inventory

# Test for Challenge 3
def test_return_coins():
    vending_machine = VendingMachine()
    vending_machine.total_amount = 5
    vending_machine.return_coins()
    assert vending_machine.total_amount == 0