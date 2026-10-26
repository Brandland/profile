<?php
/**
 * Language helpers and shared content (content/en.json, content/pt.json).
 * The same JSON drives the static prototype, so copy stays consistent.
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }

/** Current language slug: 'pt' or 'en'. Uses Polylang when active. */
function pg_lang() {
	if ( function_exists( 'pll_current_language' ) && pll_current_language( 'slug' ) ) {
		return pll_current_language( 'slug' ) === 'pt' ? 'pt' : 'en';
	}
	return strpos( determine_locale(), 'pt' ) === 0 ? 'pt' : 'en';
}

/** Load content for a language (cached). */
function pg_content( $lang = null ) {
	static $cache = array();
	$lang = $lang ? $lang : pg_lang();
	if ( ! isset( $cache[ $lang ] ) ) {
		$file           = PG_DIR . '/content/' . $lang . '.json';
		$cache[ $lang ] = file_exists( $file ) ? json_decode( file_get_contents( $file ), true ) : array();
	}
	return $cache[ $lang ];
}

/** Get a value by dot path, e.g. pg_t('home.title_html'). */
function pg_t( $path, $default = '' ) {
	$node = pg_content();
	foreach ( explode( '.', $path ) as $key ) {
		if ( ! is_array( $node ) || ! array_key_exists( $key, $node ) ) {
			return $default;
		}
		$node = $node[ $key ];
	}
	return $node;
}

/** Echo an escaped string from content. */
function pg_e( $path ) {
	echo esc_html( pg_t( $path ) );
}

/** Theme option (Customizer). */
function pg_option( $key, $default = '' ) {
	$site     = json_decode( (string) @file_get_contents( PG_DIR . '/content/site.json' ), true );
	$defaults = array(
		'linkedin_url'        => isset( $site['linkedin_url'] ) ? $site['linkedin_url'] : '',
		'linkedin_partner_id' => '',
		'linkedin_posts'      => '',
		'contact_email'       => get_option( 'admin_email' ),
	);
	return get_theme_mod( 'pg_' . $key, isset( $defaults[ $key ] ) ? $defaults[ $key ] : $default );
}

/**
 * URL of a site section in the current language.
 * Pages are found by their page template (page-expertise.php etc.).
 */
function pg_url( $key ) {
	if ( 'index' === $key ) {
		return function_exists( 'pll_home_url' ) ? pll_home_url() : home_url( '/' );
	}
	if ( 'work' === $key ) {
		$url = get_post_type_archive_link( 'case_study' );
		return $url ? $url : home_url( '/' );
	}
	if ( 'insights' === $key ) {
		$id = (int) get_option( 'page_for_posts' );
		if ( $id && function_exists( 'pll_get_post' ) ) {
			$id = pll_get_post( $id ) ? pll_get_post( $id ) : $id;
		}
		return $id ? get_permalink( $id ) : home_url( '/' );
	}
	$args = array(
		'post_type'      => 'page',
		'posts_per_page' => 1,
		'meta_key'       => '_wp_page_template',
		'meta_value'     => 'page-' . $key . '.php',
		'fields'         => 'ids',
	);
	if ( function_exists( 'pll_current_language' ) ) {
		$args['lang'] = pll_current_language( 'slug' );
	}
	$ids = get_posts( $args );
	return $ids ? get_permalink( $ids[0] ) : home_url( '/' );
}

/** Which nav key is the current view. */
function pg_current_key() {
	if ( is_front_page() ) { return 'index'; }
	if ( is_post_type_archive( 'case_study' ) || is_singular( 'case_study' ) || is_tax( array( 'pg_sector', 'pg_category' ) ) ) { return 'work'; }
	if ( is_home() || is_singular( 'post' ) || is_category() || is_tag() ) { return 'insights'; }
	if ( is_page() ) {
		$tpl = get_page_template_slug();
		if ( preg_match( '/page-(\w+)\.php/', (string) $tpl, $m ) ) { return $m[1]; }
	}
	return '';
}

/** Inline LinkedIn icon. */
function pg_icon_linkedin() {
	return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.45 20.45h-3.56v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.34V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/></svg>';
}
