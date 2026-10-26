<?php
/**
 * Playground theme setup.
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }

define( 'PG_VERSION', '1.0.0' );
define( 'PG_DIR', get_template_directory() );
define( 'PG_URI', get_template_directory_uri() );

require PG_DIR . '/inc/content.php';
require PG_DIR . '/inc/case-studies.php';
require PG_DIR . '/inc/linkedin.php';
require PG_DIR . '/inc/contact.php';
require PG_DIR . '/inc/setup-content.php';

add_action( 'after_setup_theme', function () {
	load_theme_textdomain( 'playground', PG_DIR . '/languages' );
	add_theme_support( 'title-tag' );
	add_theme_support( 'post-thumbnails' );
	add_theme_support( 'html5', array( 'search-form', 'gallery', 'caption', 'style', 'script' ) );
	add_theme_support( 'responsive-embeds' );
	add_theme_support( 'editor-styles' );
	add_image_size( 'pg-card', 1200, 800, true );
	add_image_size( 'pg-cover', 2000, 1100, true );
	register_nav_menus( array(
		'primary' => __( 'Primary menu', 'playground' ),
		'footer'  => __( 'Footer menu', 'playground' ),
	) );
} );

add_action( 'wp_enqueue_scripts', function () {
	wp_enqueue_style( 'playground', PG_URI . '/css/styles.css', array(), PG_VERSION );
	wp_enqueue_script( 'playground', PG_URI . '/js/script.js', array(), PG_VERSION, array( 'strategy' => 'defer', 'in_footer' => true ) );
	wp_add_inline_script( 'playground', 'window.PG=' . wp_json_encode( array(
		'linkedinPartnerId' => pg_option( 'linkedin_partner_id' ),
	) ) . ';', 'before' );
} );

/* Preload hero image and add hreflang (Polylang adds hreflang itself when active). */
add_action( 'wp_head', function () {
	if ( is_front_page() ) {
		echo '<link rel="preload" href="' . esc_url( PG_URI . '/assets/hero-space.webp' ) . '" as="image">' . "\n";
	}
	echo '<meta name="theme-color" content="#ffffff">' . "\n";
	$desc = is_singular() && has_excerpt() ? get_the_excerpt() : pg_t( 'pages.index.description' );
	echo '<meta name="description" content="' . esc_attr( wp_strip_all_tags( $desc ) ) . '">' . "\n";
	echo '<meta property="og:title" content="' . esc_attr( wp_get_document_title() ) . '">' . "\n";
	echo '<meta property="og:description" content="' . esc_attr( wp_strip_all_tags( $desc ) ) . '">' . "\n";
	$img = is_singular() && has_post_thumbnail() ? get_the_post_thumbnail_url( null, 'pg-cover' ) : PG_URI . '/assets/hero-space.webp';
	echo '<meta property="og:image" content="' . esc_url( $img ) . '">' . "\n";
	echo '<meta name="twitter:card" content="summary_large_image">' . "\n";
	$org = array(
		'@context' => 'https://schema.org',
		'@type'    => 'Organization',
		'name'     => 'Playground',
		'url'      => home_url( '/' ),
		'logo'     => PG_URI . '/assets/playground-logo.png',
		'sameAs'   => array_filter( array( pg_option( 'linkedin_url' ) ) ),
	);
	echo '<script type="application/ld+json">' . wp_json_encode( $org ) . '</script>' . "\n";
}, 2 );

add_filter( 'excerpt_length', function () { return 26; } );
add_filter( 'excerpt_more', function () { return '…'; } );

/** Estimated reading time in minutes. */
function pg_reading_time( $post = null ) {
	$words = str_word_count( wp_strip_all_tags( get_post_field( 'post_content', $post ) ) );
	return max( 1, (int) ceil( $words / 220 ) );
}
