<?php
get_header();
while ( have_posts() ) :
	the_post();
	$id = get_the_ID();
	$L  = pg_t( 'case_labels' );
	$sector = get_the_terms( $id, 'pg_sector' );
	$sector = ( $sector && ! is_wp_error( $sector ) ) ? $sector[0]->name : '';
	?>
<section class="case-hero"><div class="container">
<a class="crumb" href="<?php echo esc_url( pg_url( 'work' ) ); ?>">← <?php pg_e( 'ui.back_to_work' ); ?></a>
<div class="eyebrow orange reveal"><?php echo esc_html( pg_case( 'tag' ) ); ?></div>
<h1 class="h1" data-split style="margin-top:16px"><?php the_title(); ?></h1>
<?php if ( has_excerpt() ) : ?><p class="lead reveal" style="margin-top:24px"><?php echo esc_html( get_the_excerpt() ); ?></p><?php endif; ?>
<?php if ( pg_case( 'draft' ) && current_user_can( 'edit_posts' ) ) : ?><div class="draft-badge">● <?php pg_e( 'ui.draft_note' ); ?></div><?php endif; ?>
<div class="case-meta reveal">
<?php foreach ( array( 'client' => pg_case( 'client' ), 'sector' => $sector, 'year' => pg_case( 'year' ), 'location' => pg_case( 'location' ) ) as $k => $v ) : if ( $v ) : ?>
<div><small><?php echo esc_html( $L[ $k ] ); ?></small><strong><?php echo esc_html( $v ); ?></strong></div>
<?php endif; endforeach; ?>
</div></div></section>
<section><div class="container"><div class="case-cover"><?php echo pg_case_media( $id, 'case-media', 'pg-cover' ); // phpcs:ignore ?></div></div></section>
<section class="section tight"><div class="container">
<?php if ( pg_case( 'challenge' ) ) : ?><div class="case-section reveal"><h2><?php echo esc_html( $L['challenge'] ); ?></h2><p><?php echo esc_html( pg_case( 'challenge' ) ); ?></p></div><?php endif; ?>
<?php if ( pg_case( 'approach' ) ) : ?><div class="case-section reveal"><h2><?php echo esc_html( $L['approach'] ); ?></h2><div>
<?php if ( pg_case( 'quote' ) ) : ?><div class="quote reveal" style="margin:0 0 20px"><p>“<?php echo esc_html( pg_case( 'quote' ) ); ?>”</p><span><?php echo esc_html( pg_case( 'quote_by' ) ); ?></span></div><?php endif; ?>
<p><?php echo esc_html( pg_case( 'approach' ) ); ?></p></div></div><?php endif; ?>
<?php if ( pg_case( 'delivered' ) ) : ?><div class="case-section reveal"><h2><?php echo esc_html( $L['delivered'] ); ?></h2><ul class="deliver-list"><?php foreach ( pg_case( 'delivered' ) as $d ) { echo '<li>' . esc_html( $d ) . '</li>'; } ?></ul></div><?php endif; ?>
<?php if ( pg_case( 'services' ) ) : ?><div class="case-section reveal"><h2><?php echo esc_html( $L['services'] ); ?></h2><div class="pill-row" style="margin-top:0"><?php foreach ( pg_case( 'services' ) as $s ) { echo '<span class="pill">' . esc_html( $s ) . '</span>'; } ?></div></div><?php endif; ?>
<?php if ( get_the_content() ) : ?><div class="case-section reveal"><div></div><div class="article plain"><?php the_content(); ?></div></div><?php endif; ?>
</div></section>
<?php if ( pg_case( 'results' ) ) : ?>
<section class="section dark tight"><div class="container"><div class="eyebrow orange reveal"><?php echo esc_html( $L['results'] ); ?></div><div class="case-results reveal" style="margin-top:24px">
<?php foreach ( pg_case( 'results' ) as $r ) : $parts = array_map( 'trim', explode( '|', $r, 2 ) ); ?><div><strong><?php echo esc_html( $parts[0] ); ?></strong><span><?php echo esc_html( isset( $parts[1] ) ? $parts[1] : '' ); ?></span></div><?php endforeach; ?>
</div></div></section>
<?php endif; ?>
<section class="section tight"><div class="container">
<?php get_template_part( 'template-parts/share' ); ?>
<?php
$next = get_adjacent_post( false, '', false );
if ( ! $next ) { $first = get_posts( array( 'post_type' => 'case_study', 'posts_per_page' => 1, 'order' => 'ASC', 'exclude' => array( $id ) ) ); $next = $first ? $first[0] : null; }
if ( $next ) : ?>
<a class="case-next reveal" style="margin-top:40px" href="<?php echo esc_url( get_permalink( $next ) ); ?>"><div><div class="eyebrow orange"><?php pg_e( 'ui.next_case' ); ?></div><h2 class="h3" style="margin-top:12px"><?php echo esc_html( get_the_title( $next ) ); ?></h2></div><span class="arrow-big">↗</span></a>
<?php endif; ?>
</div></section>
<?php endwhile; get_footer(); ?>
