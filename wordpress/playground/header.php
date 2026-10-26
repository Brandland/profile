<!doctype html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo( 'charset' ); ?>">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="<?php echo esc_url( PG_URI . '/assets/favicon.png' ); ?>">
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<a class="skip" href="#main"><?php pg_e( 'ui.skip' ); ?></a>
<div class="scroll-progress" aria-hidden="true"></div>
<header class="site-header"><div class="nav-wrap">
<a class="brand" href="<?php echo esc_url( pg_url( 'index' ) ); ?>" aria-label="<?php echo esc_attr( pg_t( 'ui.home_aria' ) ); ?>"><img src="<?php echo esc_url( PG_URI . '/assets/playground-logo.png' ); ?>" alt="Playground" width="190" height="55"></a>
<nav class="nav-links" aria-label="Primary">
<?php
$current = pg_current_key();
$locs    = get_nav_menu_locations();
if ( ! empty( $locs['primary'] ) && ( $items = wp_get_nav_menu_items( $locs['primary'] ) ) ) {
	foreach ( $items as $item ) {
		if ( $item->menu_item_parent ) { continue; }
		$is = untrailingslashit( $item->url ) === untrailingslashit( home_url( add_query_arg( array() ) ) );
		echo '<a ' . ( $is ? 'aria-current="page" ' : '' ) . 'href="' . esc_url( $item->url ) . '">' . esc_html( $item->title ) . '</a>';
	}
} else {
	foreach ( array( 'index', 'expertise', 'sectors', 'work', 'about', 'insights', 'contact' ) as $key ) {
		echo '<a ' . ( $current === $key ? 'aria-current="page" ' : '' ) . 'href="' . esc_url( pg_url( $key ) ) . '">' . esc_html( pg_t( 'ui.nav.' . $key ) ) . '</a>';
	}
}
?>
</nav>
<div class="nav-right">
<?php if ( function_exists( 'pll_the_languages' ) ) :
	$langs = pll_the_languages( array( 'raw' => 1, 'hide_if_empty' => 0 ) ); ?>
<div class="lang-switch" role="group" aria-label="<?php echo esc_attr( pg_t( 'ui.lang_switch_label' ) ); ?>">
<?php foreach ( (array) $langs as $l ) : ?>
<a href="<?php echo esc_url( $l['url'] ); ?>" hreflang="<?php echo esc_attr( $l['slug'] ); ?>" lang="<?php echo esc_attr( $l['slug'] ); ?>"<?php echo ! empty( $l['current_lang'] ) ? ' aria-current="true"' : ''; ?>><?php echo esc_html( strtoupper( $l['slug'] ) ); ?></a>
<?php endforeach; ?>
</div>
<?php endif; ?>
<a class="nav-cta desktop magnetic" href="<?php echo esc_url( pg_url( 'contact' ) ); ?>"><?php pg_e( 'ui.cta' ); ?> <span>↗</span></a>
<button class="menu-toggle" aria-label="<?php echo esc_attr( pg_t( 'ui.menu_open' ) ); ?>" aria-expanded="false"><span></span><span></span></button>
</div>
</div></header>
<main id="main">
