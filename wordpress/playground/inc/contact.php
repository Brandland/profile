<?php
/**
 * Contact form handler (no plugin needed). Posts to admin-post.php,
 * checks nonce, honeypot and consent, then emails the recipient set in the Customizer.
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }

function pg_handle_contact() {
	$back = wp_get_referer() ? wp_get_referer() : home_url( '/' );
	if ( ! isset( $_POST['pg_contact_nonce'] ) || ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['pg_contact_nonce'] ) ), 'pg_contact' ) ) {
		wp_safe_redirect( add_query_arg( 'sent', 'error', $back ) );
		exit;
	}
	if ( ! empty( $_POST['website'] ) ) { // honeypot
		wp_safe_redirect( add_query_arg( 'sent', '1', $back ) );
		exit;
	}
	$name    = sanitize_text_field( wp_unslash( $_POST['name'] ?? '' ) );
	$email   = sanitize_email( wp_unslash( $_POST['email'] ?? '' ) );
	$message = sanitize_textarea_field( wp_unslash( $_POST['message'] ?? '' ) );
	if ( ! $name || ! is_email( $email ) || ! $message || empty( $_POST['consent'] ) ) {
		wp_safe_redirect( add_query_arg( 'sent', 'error', $back ) );
		exit;
	}
	$body = sprintf(
		"Name: %s\nOrganisation: %s\nEmail: %s\nPhone: %s\nInterest: %s\nLanguage: %s\n\n%s",
		$name,
		sanitize_text_field( wp_unslash( $_POST['company'] ?? '' ) ),
		$email,
		sanitize_text_field( wp_unslash( $_POST['phone'] ?? '' ) ),
		sanitize_text_field( wp_unslash( $_POST['interest'] ?? '' ) ),
		sanitize_text_field( wp_unslash( $_POST['lang'] ?? '' ) ),
		$message
	);
	wp_mail( pg_option( 'contact_email' ), '[Playground website] ' . $name, $body, array( 'Reply-To: ' . $name . ' <' . $email . '>' ) );
	wp_safe_redirect( add_query_arg( 'sent', '1', $back ) . '#contact-form' );
	exit;
}
add_action( 'admin_post_nopriv_pg_contact', 'pg_handle_contact' );
add_action( 'admin_post_pg_contact', 'pg_handle_contact' );
