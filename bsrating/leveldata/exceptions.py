class TimeOutError(Exception):

    def __init__(self, msg : str, time : float):
        
        super().__init__(msg)
        self.time = time

    
class MapNotFoundError(Exception):

    def __init__(self, msg : str):
        
        super().__init__(msg)

class MapLogicError(Exception):

    def __init__(self, msg : str):
        
        super().__init__(msg)