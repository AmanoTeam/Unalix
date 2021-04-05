from .objects import List


class Domains(List):


    def add_domain(self, domain: str) -> None:

        if domain not in self:
            self.append(domain)

