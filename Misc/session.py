from flask import session, redirect, url_for

class SessionManager:
    def __init__(self, session_key='username'):
        self.session_key = session_key

    def set_user_session(self, username):
        """Set session with username after successful login."""
        session[self.session_key] = username
        session.permanent = True

    def is_user_logged_in(self):
        """Check if user session is active."""
        return self.session_key in session

    def get_logged_in_user(self):
        """Retrieve the logged-in user's username from the session."""
        return session.get(self.session_key)

    def clear_user_session(self):
        """Clear the user session on logout."""
        session.pop(self.session_key, None)

    def redirect_if_not_logged_in(self, route_name='login'):
        """Redirect user to login if not logged in."""
        if not self.is_user_logged_in():
            return redirect(url_for(route_name))
