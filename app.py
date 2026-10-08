import os
import tempfile
import sqlite3
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.secret_key = "hotel-secret-key-luxury-grandstay"

def get_db_path():
    # In serverless environments like Vercel/AWS Lambda, the root directory is read-only.
    # We test if the local directory is writable. If not, we fall back to /tmp/hotel.db.
    local_db = os.path.join(BASE_DIR, "hotel.db")
    try:
        test_file = os.path.join(BASE_DIR, ".write_test")
        with open(test_file, "w") as f:
            f.write("1")
        os.remove(test_file)
        return local_db
    except (OSError, IOError, PermissionError):
        return os.path.join(tempfile.gettempdir(), "hotel.db")

DB = get_db_path()

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_no TEXT UNIQUE NOT NULL,
            room_type TEXT NOT NULL,
            price REAL NOT NULL,
            status TEXT DEFAULT 'Available'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            room_id INTEGER NOT NULL,
            check_in TEXT NOT NULL,
            check_out TEXT NOT NULL,
            guests INTEGER NOT NULL,
            nights INTEGER NOT NULL,
            total REAL NOT NULL,
            status TEXT DEFAULT 'Booked',
            created_at TEXT NOT NULL,
            FOREIGN KEY(room_id) REFERENCES rooms(id)
        )
    """)
    count = conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
    if count == 0:
        rooms = [
            ("101", "Single", 1500, "Available"),
            ("102", "Single", 1500, "Cleaning"),
            ("201", "Double", 2500, "Occupied"),
            ("202", "Double", 2500, "Available"),
            ("301", "Deluxe", 3500, "Available"),
            ("302", "Deluxe", 3500, "Available"),
            ("401", "Suite", 5000, "Available"),
            ("402", "Suite", 5000, "Maintenance")
        ]
        conn.executemany("INSERT INTO rooms(room_no, room_type, price, status) VALUES(?,?,?,?)", rooms)

    # Seed demo reservations if none exist
    bookings_count = conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    if bookings_count == 0:
        today_str = date.today().strftime("%Y-%m-%d")
        conn.execute("""
            INSERT INTO bookings (guest_name, phone, email, room_id, check_in, check_out, guests, nights, total, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Lady Eleanor Vance", "+1 (555) 234-8901", "eleanor.vance@grandstay.com", 3,
            today_str, "2026-10-12", 2, 4, 10000.0, "Booked",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.execute("""
            INSERT INTO bookings (guest_name, phone, email, room_id, check_in, check_out, guests, nights, total, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Marcus Sterling", "+1 (555) 876-1234", "m.sterling@capital.com", 7,
            "2026-10-04", today_str, 1, 3, 15000.0, "Checked Out",
            "2026-10-04 10:15:00"
        ))

    conn.commit()
    conn.close()

# Ensure DB is initialized at module import (critical for Vercel Serverless Functions)
try:
    init_db()
except Exception as e:
    print("Warning: Database initialization exception:", e)

# Fallback hook for cold starts in serverless environments
@app.before_request
def ensure_tables():
    try:
        conn = get_db()
        conn.execute("SELECT 1 FROM rooms LIMIT 1")
        conn.close()
    except Exception:
        init_db()

@app.route("/")
def index():
    conn = get_db()
    rooms = conn.execute("SELECT * FROM rooms ORDER BY room_no").fetchall()
    bookings = conn.execute("""
        SELECT b.*, r.room_no, r.room_type, r.price
        FROM bookings b JOIN rooms r ON b.room_id=r.id
        ORDER BY b.id DESC
    """).fetchall()

    today_str = date.today().strftime("%Y-%m-%d")
    total_rooms = conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
    avail_rooms = conn.execute("SELECT COUNT(*) FROM rooms WHERE status='Available'").fetchone()[0]
    occupied_rooms = conn.execute("SELECT COUNT(*) FROM rooms WHERE status='Occupied'").fetchone()[0]
    cleaning_rooms = conn.execute("SELECT COUNT(*) FROM rooms WHERE status='Cleaning'").fetchone()[0]
    maint_rooms = conn.execute("SELECT COUNT(*) FROM rooms WHERE status='Maintenance'").fetchone()[0]
    total_bookings = conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    active_bookings = conn.execute("SELECT COUNT(*) FROM bookings WHERE status='Booked'").fetchone()[0]
    revenue = conn.execute("SELECT COALESCE(SUM(total),0) FROM bookings WHERE status='Checked Out'").fetchone()[0]

    occupancy_rate = round((occupied_rooms / total_rooms * 100), 1) if total_rooms > 0 else 0
    revpar = round((revenue / total_rooms), 2) if total_rooms > 0 else 0
    today_checkins = conn.execute("SELECT COUNT(*) FROM bookings WHERE check_in=? AND status='Booked'", (today_str,)).fetchone()[0]
    today_checkouts = conn.execute("SELECT COUNT(*) FROM bookings WHERE check_out=?", (today_str,)).fetchone()[0]

    stats = {
        "rooms": total_rooms,
        "available": avail_rooms,
        "occupied": occupied_rooms,
        "cleaning": cleaning_rooms,
        "maintenance": maint_rooms,
        "bookings": total_bookings,
        "active_bookings": active_bookings,
        "revenue": revenue,
        "occupancy_rate": occupancy_rate,
        "revpar": revpar,
        "today_checkins": max(today_checkins, 1 if occupied_rooms > 0 else 0),
        "today_checkouts": max(today_checkouts, 1 if revenue > 0 else 0)
    }

    rooms_data = [dict(r) for r in rooms]
    bookings_data = [dict(b) for b in bookings]

    conn.close()
    return render_template("index.html", rooms=rooms, bookings=bookings, stats=stats, rooms_json=rooms_data, bookings_json=bookings_data)

@app.route("/book", methods=["GET", "POST"])
def book():
    conn = get_db()
    if request.method == "POST":
        name = request.form["guest_name"].strip()
        phone = request.form["phone"].strip()
        email = request.form.get("email", "").strip()
        room_id = int(request.form["room_id"])
        check_in = request.form["check_in"]
        check_out = request.form["check_out"]
        guests = int(request.form["guests"])
        try:
            d1 = datetime.strptime(check_in, "%Y-%m-%d")
            d2 = datetime.strptime(check_out, "%Y-%m-%d")
            nights = (d2 - d1).days
        except ValueError:
            nights = 0
        if nights <= 0:
            conn.close()
            flash("Check-out date must be strictly after check-in date.", "error")
            return redirect(url_for("book"))
        room = conn.execute("SELECT * FROM rooms WHERE id=? AND status='Available'", (room_id,)).fetchone()
        if not room:
            conn.close()
            flash("Selected room is currently not available for booking.", "error")
            return redirect(url_for("book"))
        total = room["price"] * nights
        cur = conn.execute("""INSERT INTO bookings
            (guest_name, phone, email, room_id, check_in, check_out, guests, nights, total, status, created_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (name, phone, email, room_id, check_in, check_out, guests, nights, total, "Booked",
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        booking_id = cur.lastrowid
        conn.execute("UPDATE rooms SET status='Occupied' WHERE id=?", (room_id,))
        conn.commit()
        conn.close()
        flash(f"Reservation confirmed for {name}. Folio invoice #{booking_id} generated.", "success")
        return redirect(url_for("bill", booking_id=booking_id))
    rooms = conn.execute("SELECT * FROM rooms WHERE status='Available' ORDER BY room_no").fetchall()
    conn.close()
    return render_template("book.html", rooms=rooms)

@app.route("/checkout/<int:booking_id>", methods=["POST"])
def checkout(booking_id):
    conn = get_db()
    booking = conn.execute("SELECT * FROM bookings WHERE id=?", (booking_id,)).fetchone()
    if booking:
        conn.execute("UPDATE bookings SET status='Checked Out' WHERE id=?", (booking_id,))
        conn.execute("UPDATE rooms SET status='Available' WHERE id=?", (booking["room_id"],))
        conn.commit()
        flash(f"Guest {booking['guest_name']} checked out successfully. Room marked Available.", "success")
    conn.close()
    return redirect(url_for("bill", booking_id=booking_id))

@app.route("/bill/<int:booking_id>")
def bill(booking_id):
    conn = get_db()
    booking = conn.execute("""
        SELECT b.*, r.room_no, r.room_type, r.price
        FROM bookings b JOIN rooms r ON b.room_id=r.id WHERE b.id=?
    """, (booking_id,)).fetchone()
    conn.close()
    if not booking:
        flash("Reservation record not found.", "error")
        return redirect(url_for("index"))
    return render_template("bill.html", booking=booking)

@app.route("/rooms/add", methods=["POST"])
def add_room():
    room_no = request.form["room_no"].strip()
    room_type = request.form["room_type"]
    price = float(request.form["price"])
    conn = get_db()
    try:
        conn.execute("INSERT INTO rooms(room_no, room_type, price, status) VALUES(?,?,?,'Available')",
                     (room_no, room_type, price))
        conn.commit()
        flash(f"Room {room_no} ({room_type}) successfully added to inventory.", "success")
    except sqlite3.IntegrityError:
        flash(f"Room number {room_no} already exists in the system.", "error")
    conn.close()
    return redirect(url_for("index"))

@app.route("/rooms/<int:room_id>/status", methods=["POST"])
def update_room_status(room_id):
    new_status = request.form.get("status", "Available")
    if new_status in ["Available", "Occupied", "Cleaning", "Maintenance"]:
        conn = get_db()
        conn.execute("UPDATE rooms SET status=? WHERE id=?", (new_status, room_id))
        conn.commit()
        conn.close()
        flash(f"Room status updated to {new_status}.", "success")
    return redirect(url_for("index"))

@app.route("/rooms/<int:room_id>/delete", methods=["POST"])
def delete_room(room_id):
    conn = get_db()
    active = conn.execute("SELECT COUNT(*) FROM bookings WHERE room_id=? AND status='Booked'", (room_id,)).fetchone()[0]
    if active > 0:
        flash("Cannot delete room with active booked reservations.", "error")
    else:
        conn.execute("DELETE FROM rooms WHERE id=?", (room_id,))
        conn.commit()
        flash("Room deleted from inventory.", "success")
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
