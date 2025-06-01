# UbuntuCycle - Community Sharing Platform

**Motto:** "You have a problem with wasting money. Don't let that guilt stop you from at least benefiting the ones around you."

## 1. Overview

UbuntuCycle is a small-scale, MVP (Minimum Viable Product) web application designed to facilitate the sharing of unwanted household items within a close-knit community, specifically initiated for a group of teachers in South Africa. The primary goal is to reduce waste and allow items collected by those with more to benefit those with less, minimizing the friction and guilt often associated with decluttering.

For its initial version, the application focuses on a single "Sharer" (the admin) posting items from their house. These items are then displayed on a public "marketplace" where community members (Claimers) can view and claim them. The physical exchange of items is handled offline (e.g., a pre-arranged meetup at a school).

This project is built with simplicity and rapid development in mind, prioritizing core functionality over complex features.

## 2. Core Features (MVP)

*   **Admin (Sharer):**
    *   Secure admin panel to add new items (title, description, category, image).
    *   View all items and their current status.
    *   Manually update the status of items (e.g., from "Claimed" to "Gone" after pickup, or manually adjust claims).
    *   (Future: Delete items).
*   **Public (Claimer):**
    *   View a list/grid of available and claimed items.
    *   See item details (image, title, description, category, status).
    *   Claim an "Available" item by providing a name/contact detail (this note is stored for the Sharer).
*   **No User Accounts for Claimers:** Claiming is anonymous beyond the contact detail provided at the time of claim.
*   **Offline Coordination:** Item pickup logistics are managed outside the application (e.g., via WhatsApp, in-person announcements).

## 3. Tech Stack

*   **Backend:** Python 3.x, FastAPI
*   **Data Validation & Serialization:** Pydantic
*   **Database:** SQLite (via SQLAlchemy ORM)
*   **Image Hosting:** Cloudinary (free tier)
*   **Frontend:** HTML5, CSS3, Vanilla JavaScript (for basic interactions)
*   **Templating:** Jinja2 (via FastAPI)
*   **WSGI/ASGI Server:** Uvicorn

## 4. Project Structure

```
ubuntu_cycle/
├── main.py             # FastAPI app, routes, Pydantic models, DB models & logic, Cloudinary integration
├── static/
│   └── style.css       # Basic CSS for frontend styling
├── templates/
│   ├── index.html      # Public item listing and claiming page
│   └── admin.html      # Admin panel for item management
├── .env                # Environment variables (Cloudinary keys, admin credentials) - NOT committed
├── .gitignore          # Specifies intentionally untracked files that Git should ignore
├── requirements.txt    # Python package dependencies
└── ubuntucycle.db      # SQLite database file (created on first run)
```

## 5. Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd ubuntu_cycle
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    Expected `requirements.txt` content:
    ```
    fastapi
    uvicorn[standard]
    pydantic
    sqlalchemy
    python-dotenv
    cloudinary
    jinja2
    python-multipart # For file uploads
    # psycopg2-binary # (Optional, if switching to PostgreSQL later)
    ```

4.  **Set up Environment Variables:**
    Create a `.env` file in the root of the project (`ubuntu_cycle/`) with the following content. Replace placeholder values with your actual credentials.

    ```env
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME="your_cloud_name"
    CLOUDINARY_API_KEY="your_api_key"
    CLOUDINARY_API_SECRET="your_api_secret"

    # Admin Credentials (for basic auth - to be implemented)
    ADMIN_USERNAME="your_admin_username"
    ADMIN_PASSWORD="your_admin_password"
    ```
    *   Sign up for a free Cloudinary account to get your API credentials.

5.  **Database Initialization:**
    The SQLite database (`ubuntucycle.db`) and its tables will be created automatically when the FastAPI application first starts, due to the `Base.metadata.create_all(bind=engine)` line in `main.py`.

## 6. Running the Application

To run the development server:
```bash
uvicorn main:app --reload
```
The application will typically be available at `http://127.0.0.1:8000`.
*   Public view: `http://127.0.0.1:8000/`
*   Admin panel: `http://127.0.0.1:8000/admin` (Note: Admin authentication is a TODO)

## 7. Key Code Components (in `main.py`)

### 7.1. Pydantic Models (Data Schemas)

```python
# Item Status Enum
class ItemStatusEnum(str, enum.Enum):
    AVAILABLE = "Available"
    CLAIMED = "Claimed"
    GONE = "Gone"

# Base model for item data
class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None

# Model for creating items (image handled separately)
class ItemCreate(ItemBase):
    pass

# Full item model for responses, including DB-generated fields
class Item(ItemBase):
    id: uuid.UUID # Or str if using string UUIDs directly
    image_url: Optional[HttpUrl] = None
    status: ItemStatusEnum = ItemStatusEnum.AVAILABLE
    claimed_by_note: Optional[str] = None
    date_posted: datetime

    class Config:
        orm_mode = True
```

### 7.2. SQLAlchemy DB Model (`DBItem`)

```python
class DBItem(Base):
    __tablename__ = "items"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, index=True)
    # ... other fields corresponding to Pydantic's Item model ...
    status = Column(DBEnum(ItemStatusEnum), default=ItemStatusEnum.AVAILABLE)
    date_posted = Column(DateTime, default=datetime.utcnow)
```
(`engine`, `SessionLocal`, and `Base` are set up for SQLite.)

### 7.3. Core API Endpoints

*   **Public:**
    *   `GET /`: Serves `index.html` displaying available and claimed items.
        *   Context: `items` (list of `Item` objects), `item_status_enum`, `now`.
    *   `POST /items/{item_id}/claim`: Allows a user to claim an item.
        *   Request: Form data with `claimer_info: str`.
        *   Action: Updates item status to "Claimed" and stores `claimer_info`.
        *   Response: JSON confirmation or updated item data.
*   **Admin (TODO: Secure these endpoints):**
    *   `GET /admin`: Serves `admin.html` for item management.
        *   Context: `items` (list of all `Item` objects), `item_status_enum`, `now`.
    *   `POST /admin/items/add`: Adds a new item.
        *   Request: Form data with `title`, `description`, `category`, and `image` (file upload).
        *   Action: Uploads image to Cloudinary, saves item details to DB.
        *   Response: Redirect to `/admin`.
    *   `POST /admin/items/{item_id}/update_status`: Updates an item's status and `claimed_by_note`.
        *   Request: Form data with `status: ItemStatusEnum` and `claimed_by_note: Optional[str]`.
        *   Action: Updates the specified item in the DB.
        *   Response: Redirect to `/admin`.

### 7.4. Cloudinary Integration

*   Configured in `main.py` using environment variables.
*   The `admin_add_item` endpoint handles uploading the image file to Cloudinary and stores the `secure_url` in the database.

### 7.5. Frontend Templates

*   `templates/index.html`:
    *   Displays items in a grid.
    *   Includes a form for each "Available" item to allow claiming.
    *   Uses JavaScript (`submitClaim` function) to handle claim submissions via `fetch` API.
*   `templates/admin.html`:
    *   Form to add new items (including file upload).
    *   Lists all items with forms to update their status and claimed_by note.

## 8. Admin Authentication (Current Status & TODO)

*   **Current:** No authentication is implemented for `/admin` routes in the provided `main.py` snippets. This is a critical security gap.
*   **TODO:** Implement basic HTTP authentication or a simple session-based login for all admin-related endpoints. The `.env` file has placeholders for `ADMIN_USERNAME` and `ADMIN_PASSWORD`. FastAPI offers utilities for this.

## 9. Future Considerations / Next Steps

*   **Implement Admin Authentication:** Top priority.
*   **Implement Item Deletion:** Add functionality for admins to delete items.
*   **Refine Frontend Styling & UX:** Improve the visual appearance and user experience.
*   **Error Handling:** Enhance error handling and user feedback on both frontend and backend.
*   **Filtering/Sorting:** Allow users to filter items by category or sort them on the public page.
*   **Pagination:** For when the number of items grows large.
*   **User Accounts (Optional - Phase 2):** If the community grows or requires more robust claim tracking, consider adding user accounts for Claimers.
*   **Notifications:** (e.g., email to admin when an item is claimed - could use a service like SendGrid).
*   **Refactor `main.py`:** As the application grows, split `main.py` into dedicated files for models (`models.py`), database interactions (`database.py`), CRUD operations (`crud.py`), and routes/routers (`routers/`).

## 10. Contributing

This is currently a small, focused project. For significant changes or feature additions, please discuss them first. Simple bug fixes or documentation improvements are welcome.

---

This README aims to provide a comprehensive starting point.