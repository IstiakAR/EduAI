"""
Test suite for authentication endpoints.
"""
import pytest
from httpx import AsyncClient
from tests.conftest import assert_response_success, assert_response_error


class TestAuthentication:
    """Test authentication endpoints."""
    
    def test_register_user_success(self, client, sample_user):
        """Test successful user registration."""
        response = client.post("/api/v1/auth/register", json=sample_user)
        assert_response_success(response, 201)
        
        data = response.json()
        assert data["email"] == sample_user["email"]
        assert data["username"] == sample_user["username"]
        assert data["full_name"] == sample_user["full_name"]
        assert "id" in data
        assert "hashed_password" not in data
    
    def test_register_duplicate_email(self, client, sample_user):
        """Test registration with duplicate email."""
        # Register first user
        response = client.post("/api/v1/auth/register", json=sample_user)
        assert_response_success(response, 201)
        
        # Try to register with same email
        response = client.post("/api/v1/auth/register", json=sample_user)
        assert_response_error(response, 400, "already registered")
    
    def test_register_invalid_email(self, client, sample_user):
        """Test registration with invalid email."""
        sample_user["email"] = "invalid-email"
        response = client.post("/api/v1/auth/register", json=sample_user)
        assert_response_error(response, 422)
    
    def test_register_weak_password(self, client, sample_user):
        """Test registration with weak password."""
        sample_user["password"] = "123"
        response = client.post("/api/v1/auth/register", json=sample_user)
        assert_response_error(response, 422)
    
    def test_login_success(self, client, sample_user):
        """Test successful login."""
        # Register user first
        client.post("/api/v1/auth/register", json=sample_user)
        
        # Login
        login_data = {
            "username": sample_user["email"],
            "password": sample_user["password"]
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert_response_success(response)
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client, sample_user):
        """Test login with invalid credentials."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert_response_error(response, 401, "Invalid credentials")
    
    def test_login_with_username(self, client, sample_user):
        """Test login with username instead of email."""
        # Register user first
        client.post("/api/v1/auth/register", json=sample_user)
        
        # Login with username
        login_data = {
            "username": sample_user["username"],
            "password": sample_user["password"]
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert_response_success(response)
    
    def test_get_profile(self, client, auth_headers):
        """Test getting user profile."""
        response = client.get("/api/v1/auth/profile", headers=auth_headers)
        assert_response_success(response)
        
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "username" in data
        assert "hashed_password" not in data
    
    def test_get_profile_unauthorized(self, client):
        """Test getting profile without authorization."""
        response = client.get("/api/v1/auth/profile")
        assert_response_error(response, 401)
    
    def test_update_profile(self, client, auth_headers):
        """Test updating user profile."""
        update_data = {
            "full_name": "Updated Name",
            "bio": "Updated bio"
        }
        response = client.patch("/api/v1/auth/profile", json=update_data, headers=auth_headers)
        assert_response_success(response)
        
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["bio"] == update_data["bio"]
    
    def test_refresh_token(self, client, sample_user):
        """Test token refresh."""
        # Register and login
        client.post("/api/v1/auth/register", json=sample_user)
        login_data = {
            "username": sample_user["email"],
            "password": sample_user["password"]
        }
        login_response = client.post("/api/v1/auth/login", data=login_data)
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert_response_success(response)
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_refresh_invalid_token(self, client):
        """Test refresh with invalid token."""
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid-token"})
        assert_response_error(response, 401)
    
    def test_change_password(self, client, auth_headers, sample_user):
        """Test changing password."""
        change_data = {
            "current_password": sample_user["password"],
            "new_password": "newpassword123"
        }
        response = client.post("/api/v1/auth/change-password", json=change_data, headers=auth_headers)
        assert_response_success(response)
        
        # Test login with new password
        login_data = {
            "username": sample_user["email"],
            "password": change_data["new_password"]
        }
        login_response = client.post("/api/v1/auth/login", data=login_data)
        assert_response_success(login_response)
    
    def test_change_password_wrong_current(self, client, auth_headers):
        """Test changing password with wrong current password."""
        change_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
        response = client.post("/api/v1/auth/change-password", json=change_data, headers=auth_headers)
        assert_response_error(response, 400, "Current password is incorrect")


@pytest.mark.asyncio
class TestAuthenticationAsync:
    """Test authentication endpoints with async client."""
    
    async def test_register_user_async(self, async_client, sample_user):
        """Test async user registration."""
        response = await async_client.post("/api/v1/auth/register", json=sample_user)
        assert response.status_code == 201
        
        data = response.json()
        assert data["email"] == sample_user["email"]
        assert "id" in data
    
    async def test_login_async(self, async_client, sample_user):
        """Test async login."""
        # Register user first
        await async_client.post("/api/v1/auth/register", json=sample_user)
        
        # Login
        login_data = {
            "username": sample_user["email"],
            "password": sample_user["password"]
        }
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data


class TestAuthenticationValidation:
    """Test authentication input validation."""
    
    def test_register_missing_fields(self, client):
        """Test registration with missing required fields."""
        incomplete_user = {"email": "test@example.com"}
        response = client.post("/api/v1/auth/register", json=incomplete_user)
        assert_response_error(response, 422)
    
    def test_register_empty_fields(self, client, sample_user):
        """Test registration with empty fields."""
        sample_user["username"] = ""
        response = client.post("/api/v1/auth/register", json=sample_user)
        assert_response_error(response, 422)
    
    def test_login_missing_fields(self, client):
        """Test login with missing fields."""
        incomplete_login = {"username": "test@example.com"}
        response = client.post("/api/v1/auth/login", data=incomplete_login)
        assert_response_error(response, 422)
    
    def test_update_profile_invalid_data(self, client, auth_headers):
        """Test profile update with invalid data."""
        invalid_data = {"email": "invalid-email"}
        response = client.patch("/api/v1/auth/profile", json=invalid_data, headers=auth_headers)
        assert_response_error(response, 422)