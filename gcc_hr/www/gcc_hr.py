import frappe
import frappe.sessions

no_cache = 1


def get_context(context):
	# Guests get served the same SPA shell, not a server-side redirect to
	# Frappe's own generic /login page -- the Vue app owns its own Login
	# screen (frontend/src/pages/auth/Login.vue) and client-side router
	# guard (router/index.ts), consistent with "Vue is the primary/complete
	# UI" for this app. get_csrf_token()/get_roles()/get_fullname() are all
	# safe to call for a Guest session -- they just return the Guest-facing
	# values (an empty role list, "Guest" as the full name, etc.).
	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()  # nosemgrep

	context.csrf_token = csrf_token
	context.boot = {
		"csrf_token": csrf_token,
		"user": frappe.session.user,
		"full_name": frappe.utils.get_fullname(frappe.session.user),
		"user_image": frappe.db.get_value("User", frappe.session.user, "user_image"),
		"roles": frappe.get_roles(frappe.session.user),
		"site_name": frappe.local.site,
	}

	return context
