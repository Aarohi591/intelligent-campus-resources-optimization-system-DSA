"""SAMPLE DATA - FICTIONAL.  None of this is real NIET campus data.
It exists so the prototype can be demonstrated and tested.  To use real data, replace
sample_inventory() and sample_requests() with your own list of Resource / BookingRequest objects."""
import random
from campus import *


def sample_inventory():
    F = frozenset
    return Inventory([
        # classrooms
        Resource("CR-101", "classroom", 60, equipment=F({"projector", "whiteboard"}), name="Classroom 101"),
        Resource("CR-102", "classroom", 60, equipment=F({"whiteboard"}), name="Classroom 102"),
        Resource("CR-201", "classroom", 120, equipment=F({"projector", "microphone", "whiteboard"}), name="Classroom 201"),
        # seminar hall
        Resource("AUD-1", "seminar_hall", 300, equipment=F({"projector", "microphone", "stage"}), name="Main Auditorium"),
        # laboratories
        Resource("LAB-CS1", "lab", 40, equipment=F({"computers", "projector"}), name="CS Lab 1"),
        Resource("LAB-CS2", "lab", 40, equipment=F({"computers"}), name="CS Lab 2",
                 blackouts=((at("Wed", "09:00"), at("Wed", "13:00")),)),           # network upgrade
        Resource("LAB-PHY", "lab", 30, equipment=F({"oscilloscopes"}), name="Physics Lab"),
        Resource("LAB-CHEM", "lab", 24, available=False, equipment=F({"fume_hood"}), name="Chemistry Lab"),  # out of service
        # portable projectors (bookable on their own)
        Resource("PRJ-01", "projector", 1, equipment=F({"hdmi"}), name="Portable projector 1"),
        Resource("PRJ-02", "projector", 1, equipment=F({"hdmi", "vga"}), name="Portable projector 2"),
        # sports facilities
        Resource("GRD-1", "sports_ground", 200, equipment=F({"goalposts"}), name="Main Ground", window=(6 * 60, 19 * 60)),
        Resource("CRT-BB", "indoor_court", 30, equipment=F({"floodlights", "scoreboard"}), name="Basketball Court", window=(6 * 60, 21 * 60)),
        Resource("CRT-BD", "indoor_court", 16, equipment=F({"floodlights"}), name="Badminton Hall", window=(6 * 60, 21 * 60)),
    ])


def sample_requests():
    B, F = BookingRequest, frozenset
    return [
        # --- Monday: classrooms
        B(1, "Prof. R. Sharma", "CSE", "classroom", at("Mon", "09:00"), at("Mon", "10:00"), 9, 55, F({"projector"}), purpose="Lecture"),
        B(2, "Dr. A. Khan", "ECE", "classroom", at("Mon", "09:00"), at("Mon", "11:00"), 8, 50, F({"projector"}), purpose="Lecture"),
        B(3, "Dr. P. Nair", "Maths", "classroom", at("Mon", "09:30"), at("Mon", "10:30"), 7, 55, F({"projector"}), purpose="Tutorial"),
        B(4, "Ms. S. Iyer", "English", "classroom", at("Mon", "09:00"), at("Mon", "10:00"), 4, 40, purpose="Workshop"),
        B(5, "Prof. T. Das", "Mechanical", "classroom", at("Mon", "11:00"), at("Mon", "12:00"), 6, 150, purpose="Joint lecture"),
        B(6, "Dr. L. Fernandes", "Civil", "classroom", at("Mon", "10:00"), at("Mon", "11:00"), 5, 40, F({"smartboard"}), purpose="Seminar"),
        # --- Monday: portable projectors
        B(16, "Photography Club", "Student Clubs", "projector", at("Mon", "15:00"), at("Mon", "17:00"), 3, 1, F({"hdmi"}), purpose="Photo walk review"),
        B(17, "Debate Society", "Student Clubs", "projector", at("Mon", "16:00"), at("Mon", "18:00"), 4, 1, F({"vga"}), purpose="Practice round"),
        B(18, "Dance Club", "Student Clubs", "projector", at("Mon", "16:30"), at("Mon", "17:30"), 2, 1, F({"hdmi"}), purpose="Choreography video"),
        # --- Tuesday: laboratories
        B(7, "Dr. M. Rao", "CSE", "lab", at("Tue", "14:00"), at("Tue", "17:00"), 8, 35, F({"computers"}), purpose="DSA lab, section A"),
        B(8, "Dr. N. Pillai", "IT", "lab", at("Tue", "14:00"), at("Tue", "17:00"), 8, 35, F({"computers"}), purpose="DBMS lab, section B"),
        B(9, "Mr. K. Joshi", "AI&DS", "lab", at("Tue", "14:00"), at("Tue", "17:00"), 7, 35, F({"computers"}), purpose="ML lab, section C"),
        B(10, "Dr. V. Menon", "Physics", "lab", at("Tue", "14:00"), at("Tue", "16:00"), 6, 25, F({"oscilloscopes"}), purpose="Optics practical"),
        B(11, "Dr. H. Bose", "Chemistry", "lab", at("Tue", "10:00"), at("Tue", "12:00"), 7, 20, F({"fume_hood"}), purpose="Organic practical"),
        B(12, "Mr. D. Singh", "CSE", "lab", at("Wed", "10:00"), at("Wed", "12:00"), 5, 30, F({"computers"}, ), "LAB-CS2", "Makeup lab"),
        # --- Tuesday: auditorium (one hall, three requests)
        B(13, "Student Council", "Student Affairs", "seminar_hall", at("Tue", "09:00"), at("Tue", "13:00"), 6, 200, F({"stage"}), purpose="Tech fest rehearsal"),
        B(14, "Alumni Cell", "Alumni Relations", "seminar_hall", at("Tue", "09:00"), at("Tue", "11:00"), 5, 150, F({"microphone"}), purpose="Guest lecture"),
        B(15, "Placement Cell", "Training & Placement", "seminar_hall", at("Tue", "11:00"), at("Tue", "13:00"), 5, 150, F({"microphone"}), purpose="Industry talk"),
        # --- Wednesday: sports
        B(19, "Football Team", "Sports Committee", "sports_ground", at("Wed", "16:00"), at("Wed", "18:00"), 7, 80, F({"goalposts"}), purpose="Match practice"),
        B(20, "Athletics Squad", "Sports Committee", "sports_ground", at("Wed", "17:00"), at("Wed", "19:00"), 5, 40, purpose="Track practice"),
        B(21, "Hostel Council", "Hostel Affairs", "sports_ground", at("Wed", "19:00"), at("Wed", "21:00"), 4, 40, purpose="Night football"),
        B(22, "Basketball Club", "Sports Committee", "indoor_court", at("Wed", "18:00"), at("Wed", "20:00"), 6, 20, F({"floodlights"}), purpose="Practice"),
        B(23, "Badminton Club", "Sports Committee", "indoor_court", at("Wed", "18:00"), at("Wed", "20:00"), 5, 12, F({"floodlights"}), purpose="Practice"),
        B(24, "Inter-college Meet", "Sports Committee", "indoor_court", at("Wed", "18:30"), at("Wed", "20:30"), 9, 25, F({"scoreboard", "floodlights"}), purpose="Basketball match"),
    ]


def random_requests(inv, n, seed):
    """SYNTHETIC random requests for stress tests (not realistic usage patterns)."""
    g, types = random.Random(seed), inv.types()
    gear = ["projector", "microphone", "computers", "whiteboard", "floodlights", "smartboard"]
    out = []
    for i in range(n):
        t = g.choice(types)
        biggest = max(r.capacity for r in inv.by_type(t))
        start = at(g.randrange(3), "00:00") + g.randrange(6 * 60, 20 * 60, 30)
        out.append(BookingRequest(
            i + 1, f"user{i}", f"dept{g.randrange(5)}", t, start, start + g.choice([30, 60, 90, 120, 180]),
            g.randint(1, 10), g.randint(1, int(biggest * 1.1)),
            frozenset(g.sample(gear, g.choice([0, 0, 1]))),
            g.choice([None, None, None, g.choice(inv.by_type(t)).id])))
    return out
