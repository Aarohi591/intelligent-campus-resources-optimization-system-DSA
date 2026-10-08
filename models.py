from dataclasses import dataclass


@dataclass
class Request:
    request_id: str
    requester: str
    resource: str
    start: int
    end: int
    priority: int

    def duration(self):
        return self.end - self.start

    def conflicts_with(self, other):
        if self.resource != other.resource:
            return False

        return self.start < other.end and other.start < self.end
