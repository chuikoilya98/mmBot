from instagram.inst import Inst
import os.path as pt
import json

class Parser():
    ACCS_FILENAME = pt.abspath('parser/accs.json')
    
    def getAccs(self) -> list:
        with open(self.ACCS_FILENAME, 'r') as file:
            data = json.load(file)
        
        return data

    def parsing(self) -> None:
        data = self.getAccs()
        ig = Inst()
        
        for acc in data['accs']:
            info = ig.getInfoByUser(username=acc['name'])
            print(info)



p = Parser()
p.parsing()