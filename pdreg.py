import time


class PDReg:
    def __init__(self, p_coeff, i_coeff, d_coeff):
        self.p_coeff = p_coeff
        self.i_coeff = i_coeff
        self.d_coeff = d_coeff
        self.prev_iter_time = 0
        self.dt = 0
        self.de = 0

    def compute(self, error: float) -> float:
        """Compute control signal of given PIDReg, rudimentary FBL-protection included

        Args:
            error (float): Error, based of which result will be computed
        Returns:
            float: Control signal, pass this into control sequence
        """
        self.dt = time.thread_time()
        control_signal: float = \
            self.p_coeff * error + \
            self.d_coeff * (self.de / self.dt)
        control_signal = 50 if control_signal > 100 else -50 if control_signal < -100 else control_signal
        self.de = control_signal
        return control_signal
