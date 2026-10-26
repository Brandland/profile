<?php
/* Template Name: Expertise */
get_header();
$p    = pg_t( 'expertise_page' );
$meta = '<div class="page-meta reveal">';
foreach ( $p['meta'] as $m ) { $meta .= '<div><strong>' . esc_html( $m['strong'] ) . '</strong>' . esc_html( $m['text'] ) . '</div>'; }
$meta .= '</div>';
get_template_part( 'template-parts/page-hero', null, array( 'eyebrow' => $p['eyebrow'], 'title' => $p['title'], 'lead' => $p['lead'], 'extra' => $meta ) );
?>
<section class="section"><div class="container"><div class="stack">
<?php foreach ( pg_t( 'services', array() ) as $i => $s ) : ?>
<div class="expert-row reveal" id="<?php echo esc_attr( $s['slug'] ); ?>"><span class="num"><?php printf( '%02d', $i + 1 ); ?></span><h3><?php echo esc_html( $s['title'] ); ?></h3><p><?php echo esc_html( $s['detail'] ); ?></p></div>
<?php endforeach; ?>
</div></div></section>
<?php while ( have_posts() ) : the_post(); if ( get_the_content() ) : ?><section class="section tight"><div class="container"><div class="article plain"><?php the_content(); ?></div></div></section><?php endif; endwhile; ?>
<section class="section soft"><div class="container"><div class="eyebrow orange reveal"><?php echo esc_html( $p['method_eyebrow'] ); ?></div><h2 class="h2" data-split style="margin:14px 0 40px"><?php echo esc_html( $p['method_title'] ); ?></h2>
<div class="method" data-stagger><?php foreach ( $p['method'] as $m ) : ?><div class="step reveal"><h3><?php echo esc_html( $m['title'] ); ?></h3><p><?php echo esc_html( $m['text'] ); ?></p><span class="bar"></span></div><?php endforeach; ?></div></div></section>
<?php get_template_part( 'template-parts/cta' ); get_footer(); ?>
