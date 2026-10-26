<?php
/**
 * Case study post type, taxonomies and structured fields.
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }

add_action( 'init', function () {
	register_post_type( 'case_study', array(
		'labels'       => array(
			'name'          => __( 'Case studies', 'playground' ),
			'singular_name' => __( 'Case study', 'playground' ),
			'add_new_item'  => __( 'Add case study', 'playground' ),
			'edit_item'     => __( 'Edit case study', 'playground' ),
		),
		'public'       => true,
		'has_archive'  => true,
		'rewrite'      => array( 'slug' => 'work', 'with_front' => false ),
		'menu_icon'    => 'dashicons-portfolio',
		'menu_position'=> 5,
		'show_in_rest' => true,
		'supports'     => array( 'title', 'editor', 'excerpt', 'thumbnail', 'revisions', 'page-attributes' ),
	) );
	register_taxonomy( 'pg_sector', 'case_study', array(
		'label'        => __( 'Sectors', 'playground' ),
		'hierarchical' => true,
		'show_in_rest' => true,
		'rewrite'      => array( 'slug' => 'sector' ),
	) );
	register_taxonomy( 'pg_category', 'case_study', array(
		'label'        => __( 'Work type', 'playground' ),
		'hierarchical' => true,
		'show_in_rest' => true,
		'rewrite'      => array( 'slug' => 'work-type' ),
	) );
} );

/* Make case studies and their taxonomies translatable in Polylang. */
add_filter( 'pll_get_post_types', function ( $types ) { $types['case_study'] = 'case_study'; return $types; } );
add_filter( 'pll_get_taxonomies', function ( $tax ) { $tax['pg_sector'] = 'pg_sector'; $tax['pg_category'] = 'pg_category'; return $tax; } );

/** Field definitions: key => [label, type]. */
function pg_case_fields() {
	return array(
		'client'    => array( __( 'Client (as it may be shown publicly)', 'playground' ), 'text' ),
		'year'      => array( __( 'Year', 'playground' ), 'text' ),
		'location'  => array( __( 'Location', 'playground' ), 'text' ),
		'tag'       => array( __( 'Tag line (e.g. Energy · Stakeholder engagement)', 'playground' ), 'text' ),
		'services'  => array( __( 'Services (one per line)', 'playground' ), 'lines' ),
		'challenge' => array( __( 'The challenge', 'playground' ), 'textarea' ),
		'approach'  => array( __( 'Our approach', 'playground' ), 'textarea' ),
		'delivered' => array( __( 'What we delivered (one per line)', 'playground' ), 'lines' ),
		'results'   => array( __( 'Results (one per line: value | label)', 'playground' ), 'lines' ),
		'quote'     => array( __( 'Client quote', 'playground' ), 'textarea' ),
		'quote_by'  => array( __( 'Quote attribution', 'playground' ), 'text' ),
		'media'     => array( __( 'Cover style if no featured image (space, dark, light, orbit)', 'playground' ), 'text' ),
		'draft'     => array( __( 'Show "illustrative case" badge (1 = yes)', 'playground' ), 'text' ),
	);
}

add_action( 'add_meta_boxes', function () {
	add_meta_box( 'pg_case', __( 'Case study details', 'playground' ), 'pg_case_metabox', 'case_study', 'normal', 'high' );
} );

function pg_case_metabox( $post ) {
	wp_nonce_field( 'pg_case_save', 'pg_case_nonce' );
	echo '<table class="form-table">';
	foreach ( pg_case_fields() as $key => $f ) {
		$val = get_post_meta( $post->ID, '_pg_' . $key, true );
		echo '<tr><th><label for="pg_' . esc_attr( $key ) . '">' . esc_html( $f[0] ) . '</label></th><td>';
		if ( 'text' === $f[1] ) {
			echo '<input class="widefat" type="text" id="pg_' . esc_attr( $key ) . '" name="pg_' . esc_attr( $key ) . '" value="' . esc_attr( $val ) . '">';
		} else {
			echo '<textarea class="widefat" rows="' . ( 'lines' === $f[1] ? 5 : 4 ) . '" id="pg_' . esc_attr( $key ) . '" name="pg_' . esc_attr( $key ) . '">' . esc_textarea( $val ) . '</textarea>';
		}
		echo '</td></tr>';
	}
	echo '</table>';
}

add_action( 'save_post_case_study', function ( $post_id ) {
	if ( ! isset( $_POST['pg_case_nonce'] ) || ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['pg_case_nonce'] ) ), 'pg_case_save' ) ) { return; }
	if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) { return; }
	if ( ! current_user_can( 'edit_post', $post_id ) ) { return; }
	foreach ( pg_case_fields() as $key => $f ) {
		if ( isset( $_POST[ 'pg_' . $key ] ) ) {
			$raw = wp_unslash( $_POST[ 'pg_' . $key ] );
			$val = 'text' === $f[1] ? sanitize_text_field( $raw ) : sanitize_textarea_field( $raw );
			update_post_meta( $post_id, '_pg_' . $key, $val );
		}
	}
} );

/** Read a case field. 'lines' fields return arrays. */
function pg_case( $key, $post_id = null ) {
	$post_id = $post_id ? $post_id : get_the_ID();
	$val     = (string) get_post_meta( $post_id, '_pg_' . $key, true );
	$fields  = pg_case_fields();
	if ( isset( $fields[ $key ] ) && 'lines' === $fields[ $key ][1] ) {
		return array_values( array_filter( array_map( 'trim', explode( "\n", $val ) ) ) );
	}
	return $val;
}

/** Cover markup: featured image, or a brand gradient. */
function pg_case_media( $post_id, $class = 'case-media', $size = 'pg-card' ) {
	if ( has_post_thumbnail( $post_id ) ) {
		$url = get_the_post_thumbnail_url( $post_id, $size );
		return '<div class="' . esc_attr( $class ) . '" style="background:url(' . esc_url( $url ) . ') center/cover"></div>';
	}
	$media  = pg_case( 'media', $post_id );
	$styles = array(
		'space' => 'background:url(' . PG_URI . '/assets/section-space.webp) center/cover',
		'dark'  => 'background:linear-gradient(135deg,#101010 0%,#252525 48%,#e78d39 160%)',
		'light' => 'background:linear-gradient(145deg,#f8f8f6,#d8d9dc 65%,#f08b24 190%)',
		'orbit' => 'background:radial-gradient(circle at 75% 20%,#f08b24 0%,#48220d 20%,#101010 52%,#050505 100%)',
	);
	$style = isset( $styles[ $media ] ) ? $styles[ $media ] : $styles['dark'];
	return '<div class="' . esc_attr( $class ) . '" style="' . esc_attr( $style ) . '"></div>';
}

/** First term slug of a taxonomy. */
function pg_term_slug( $post_id, $tax ) {
	$terms = get_the_terms( $post_id, $tax );
	return ( $terms && ! is_wp_error( $terms ) ) ? $terms[0]->slug : '';
}

/* Show all case studies on the archive, in editorial order. */
add_action( 'pre_get_posts', function ( $q ) {
	if ( ! is_admin() && $q->is_main_query() && ( $q->is_post_type_archive( 'case_study' ) || $q->is_tax( array( 'pg_sector', 'pg_category' ) ) ) ) {
		$q->set( 'posts_per_page', -1 );
		$q->set( 'orderby', array( 'menu_order' => 'ASC', 'date' => 'DESC' ) );
	}
} );
