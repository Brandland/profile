<?php
/**
 * LinkedIn integration:
 * - Customizer: company page URL, Insight Tag partner ID, post embeds
 * - Share buttons on posts and case studies (template-parts/share.php)
 * - "Follow the conversation" block with embedded LinkedIn posts
 * - Insight Tag loads only after cookie consent (see js/script.js)
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }

add_action( 'customize_register', function ( $wp_customize ) {
	$wp_customize->add_section( 'pg_linkedin', array(
		'title'    => __( 'Playground: LinkedIn & contact', 'playground' ),
		'priority' => 30,
	) );
	$settings = array(
		'linkedin_url'        => array( __( 'LinkedIn company page URL', 'playground' ), 'url', 'esc_url_raw' ),
		'linkedin_partner_id' => array( __( 'LinkedIn Insight Tag partner ID (optional)', 'playground' ), 'text', 'sanitize_text_field' ),
		'linkedin_posts'      => array( __( 'LinkedIn posts to feature (one embed URL or post URL per line)', 'playground' ), 'textarea', 'sanitize_textarea_field' ),
		'contact_email'       => array( __( 'Contact form recipient', 'playground' ), 'email', 'sanitize_email' ),
	);
	foreach ( $settings as $key => $s ) {
		$wp_customize->add_setting( 'pg_' . $key, array( 'default' => pg_option( $key ), 'sanitize_callback' => $s[2] ) );
		$wp_customize->add_control( 'pg_' . $key, array( 'label' => $s[0], 'section' => 'pg_linkedin', 'type' => $s[1] ) );
	}
} );

/**
 * Convert a LinkedIn post URL to its embed URL.
 * Accepts embed URLs as-is, or URLs containing urn:li:activity / share / ugcPost.
 */
function pg_linkedin_embed_url( $url ) {
	$url = trim( $url );
	if ( strpos( $url, '/embed/feed/update/' ) !== false ) {
		return $url;
	}
	if ( preg_match( '/(urn:li:(?:activity|share|ugcPost):\d+)/', rawurldecode( $url ), $m ) ) {
		return 'https://www.linkedin.com/embed/feed/update/' . $m[1];
	}
	if ( preg_match( '/activity-(\d{15,})/', $url, $m ) ) {
		return 'https://www.linkedin.com/embed/feed/update/urn:li:activity:' . $m[1];
	}
	return '';
}

/** Embedded LinkedIn posts (max 3). */
function pg_linkedin_embeds() {
	$lines = array_filter( array_map( 'trim', explode( "\n", (string) pg_option( 'linkedin_posts' ) ) ) );
	$out   = array();
	foreach ( array_slice( $lines, 0, 3 ) as $line ) {
		$src = pg_linkedin_embed_url( $line );
		if ( $src ) {
			$out[] = '<iframe src="' . esc_url( $src ) . '" title="LinkedIn post" loading="lazy" allowfullscreen></iframe>';
		}
	}
	return $out;
}

/** Shortcode: [playground_linkedin] renders the LinkedIn block anywhere. */
add_shortcode( 'playground_linkedin', function () {
	ob_start();
	get_template_part( 'template-parts/linkedin' );
	return ob_get_clean();
} );

/** Shortcode: [linkedin_share] renders share buttons for the current page. */
add_shortcode( 'linkedin_share', function () {
	ob_start();
	get_template_part( 'template-parts/share' );
	return ob_get_clean();
} );
