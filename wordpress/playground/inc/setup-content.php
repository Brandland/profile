<?php
/**
 * Tools > Playground setup: creates pages, case studies and the first insight
 * in English and Portuguese from content/*.json, and links translations in Polylang.
 * Safe to run more than once (existing items are skipped by slug).
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }

add_action( 'admin_menu', function () {
	add_management_page( 'Playground setup', 'Playground setup', 'manage_options', 'pg-setup', 'pg_setup_screen' );
} );

function pg_setup_screen() {
	$done = null;
	if ( isset( $_POST['pg_setup'] ) && check_admin_referer( 'pg_setup' ) ) {
		$done = pg_import_content();
	}
	echo '<div class="wrap"><h1>Playground setup</h1>';
	echo '<p>Creates the pages (Home, Expertise, Sectors, About, Insights, Contact, Privacy), the four case studies and the first insight article in English and Portuguese.</p>';
	echo '<p>' . ( function_exists( 'pll_set_post_language' ) ? '✅ Polylang detected. Make sure the languages English (en) and Português (pt) exist in Languages settings first.' : '⚠️ Polylang is not active. Content will be created, but translations will not be linked. Install Polylang first for the bilingual site.' ) . '</p>';
	if ( $done ) {
		echo '<div class="notice notice-success"><p>' . esc_html( $done ) . '</p></div>';
	}
	echo '<form method="post">';
	wp_nonce_field( 'pg_setup' );
	submit_button( 'Import content', 'primary', 'pg_setup' );
	echo '</form></div>';
}

function pg_setup_slugs() {
	return array(
		'en' => array( 'index' => 'home', 'expertise' => 'expertise', 'sectors' => 'sectors', 'about' => 'about', 'insights' => 'insights', 'contact' => 'contact', 'privacy' => 'privacy-policy' ),
		'pt' => array( 'index' => 'inicio', 'expertise' => 'competencias', 'sectors' => 'sectores', 'about' => 'sobre-nos', 'insights' => 'perspectivas', 'contact' => 'contacto', 'privacy' => 'politica-de-privacidade' ),
	);
}

function pg_insert_once( $args, $lang ) {
	$existing = get_page_by_path( $args['post_name'], OBJECT, $args['post_type'] );
	if ( $existing ) {
		return $existing->ID;
	}
	$id = wp_insert_post( wp_parse_args( $args, array( 'post_status' => 'publish' ) ) );
	if ( $id && ! is_wp_error( $id ) && function_exists( 'pll_set_post_language' ) ) {
		pll_set_post_language( $id, $lang );
	}
	return $id;
}

function pg_term_for( $name, $slug, $tax, $lang ) {
	$term = get_term_by( 'slug', $slug, $tax );
	if ( ! $term ) {
		$r = wp_insert_term( $name, $tax, array( 'slug' => $slug ) );
		if ( is_wp_error( $r ) ) { return 0; }
		$tid = $r['term_id'];
		if ( function_exists( 'pll_set_term_language' ) ) { pll_set_term_language( $tid, $lang ); }
		return $tid;
	}
	return $term->term_id;
}

function pg_import_content() {
	$slugs = pg_setup_slugs();
	$map   = array(); // [key][lang] => post id
	$count = 0;
	foreach ( array( 'en', 'pt' ) as $lang ) {
		$c = pg_content( $lang );
		$titles = array(
			'index'     => 'Playground',
			'expertise' => $c['ui']['nav']['expertise'],
			'sectors'   => $c['ui']['nav']['sectors'],
			'about'     => $c['ui']['nav']['about'],
			'insights'  => $c['ui']['nav']['insights'],
			'contact'   => $c['ui']['nav']['contact'],
			'privacy'   => $c['privacy_page']['title'],
		);
		foreach ( $titles as $key => $title ) {
			$content = 'privacy' === $key ? '<!-- wp:paragraph --><p>' . implode( '</p><!-- /wp:paragraph --><!-- wp:paragraph --><p>', array_map( 'esc_html', $c['privacy_page']['body'] ) ) . '</p><!-- /wp:paragraph -->' : '';
			$id = pg_insert_once( array( 'post_type' => 'page', 'post_title' => $title, 'post_name' => $slugs[ $lang ][ $key ], 'post_content' => $content ), $lang );
			if ( in_array( $key, array( 'expertise', 'sectors', 'about', 'contact' ), true ) ) {
				update_post_meta( $id, '_wp_page_template', 'page-' . $key . '.php' );
			}
			$map[ 'page_' . $key ][ $lang ] = $id;
			$count++;
		}
		// Case studies.
		foreach ( $c['cases'] as $i => $cs ) {
			$id = pg_insert_once( array(
				'post_type'    => 'case_study',
				'post_title'   => rtrim( $cs['title'], '.' ),
				'post_name'    => $cs['slug'] . ( 'pt' === $lang ? '-pt' : '' ),
				'post_excerpt' => $cs['summary'],
				'menu_order'   => $i,
			), $lang );
			$meta = array(
				'client' => $cs['client'], 'year' => $cs['year'], 'location' => $cs['location'], 'tag' => $cs['tag'],
				'services' => implode( "\n", $cs['services'] ), 'challenge' => $cs['challenge'], 'approach' => $cs['approach'],
				'delivered' => implode( "\n", $cs['delivered'] ),
				'results' => implode( "\n", array_map( function ( $r ) { return $r['value'] . ' | ' . $r['label']; }, $cs['results'] ) ),
				'quote' => $cs['quote'], 'quote_by' => $cs['quote_by'], 'media' => $cs['media'], 'draft' => ! empty( $cs['draft'] ) ? '1' : '',
			);
			foreach ( $meta as $k => $v ) { update_post_meta( $id, '_pg_' . $k, $v ); }
			$sector_name = $cs['sector'];
			foreach ( $c['sectors'] as $s ) { if ( $s['slug'] === $cs['sector'] ) { $sector_name = $s['name']; } }
			$cat_name = $cs['category'];
			foreach ( $c['work_page']['filters'] as $f ) { if ( $f['key'] === $cs['category'] ) { $cat_name = $f['label']; } }
			$suffix = 'pt' === $lang ? '-pt' : '';
			wp_set_object_terms( $id, array( (int) pg_term_for( $sector_name, $cs['sector'] . $suffix, 'pg_sector', $lang ) ), 'pg_sector' );
			wp_set_object_terms( $id, array( (int) pg_term_for( $cat_name, $cs['category'] . $suffix, 'pg_category', $lang ) ), 'pg_category' );
			$map[ 'case_' . $i ][ $lang ] = $id;
			$count++;
		}
		// First insight with body.
		foreach ( $c['insights'] as $j => $in ) {
			if ( empty( $in['body'] ) ) { continue; }
			$body = '';
			foreach ( $in['body'] as $p ) { $body .= '<!-- wp:paragraph --><p>' . esc_html( $p ) . '</p><!-- /wp:paragraph -->'; }
			$id = pg_insert_once( array( 'post_type' => 'post', 'post_title' => rtrim( $in['title'], '.' ), 'post_name' => $in['slug'] . ( 'pt' === $lang ? '-pt' : '' ), 'post_excerpt' => $in['excerpt'], 'post_content' => $body ), $lang );
			$map[ 'post_' . $j ][ $lang ] = $id;
			$count++;
		}
	}
	if ( function_exists( 'pll_save_post_translations' ) ) {
		foreach ( $map as $pair ) {
			if ( count( $pair ) === 2 ) { pll_save_post_translations( $pair ); }
		}
	}
	update_option( 'show_on_front', 'page' );
	update_option( 'page_on_front', $map['page_index']['en'] );
	update_option( 'page_for_posts', $map['page_insights']['en'] );
	flush_rewrite_rules();
	return sprintf( 'Done. %d items checked or created.', $count );
}
