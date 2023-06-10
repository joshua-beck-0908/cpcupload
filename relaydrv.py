import microcontroller
import digitalio
import board

relayPins = [board.D0, board.D1, board.D2, board.D3, board.D4, board.D5, board.D6, board.D7]

class RelayCtrl:
    def __init__(self, relay_pins) -> None:
        self.relayPins = [digitalio.DigitalInOut(pin) for pin in relayPins]
        self.relayStates = [False] * len(self.relayPins)
        for pin in self.relayPins:
            pin.direction = digitalio.Direction.OUTPUT
            pin.value = False

    def set_relay(self, relay, state) -> None: # state is a boolean
        try:
            self.relayStates[relay] = state
            self.relayPins[relay].value = state
        except IndexError:
            print('ERR: Out of range.')
        else:
            print('OK')

    def get_relay(self, relay) -> bool:
        try:
            state = self.relayStates[relay]
        except IndexError:
            print('ERR: Out of range.')
            return False
        else:
            print('OK')
            return state
    
def main():
    ctrl = RelayCtrl(relayPins)
    
    while True:
        cmd = input().upper()
        if cmd == '':
            continue
        if cmd[0] == 'S' and len(cmd) > 2:
            ctrl.set_relay(int(cmd[1]), bool(int(cmd[2])))
        elif cmd[0] == 'G' and len(cmd) > 1:
            print(ctrl.get_relay(int(cmd[1])))

if __name__ == '__main__':
    main()