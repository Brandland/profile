<?php
/* Template Name: About */
get_header();
$p = pg_t( 'about_page' );
get_template_part( 'template-parts/page-hero', null, array( 'eyebrow' => $p['eyebrow'], 'title' => $p['title'], 'lead' => $p['lead'] ) );
?>
<section class="section"><div class="container"><div class="intro-split"><div class="sticky-title"><div class="eyebrow orange reveal"><?php echo esc_html( $p['story_eyebrow'] ); ?></div><h2 class="h2" data-split style="margin-top:14px"><?php echo esc_html( $p['story_title'] ); ?></h2></div>
<div><?php foreach ( $p['story'] as $s ) { echo '<p class="copy reveal">' . esc_html( $s ) . '</p>'; } ?><?php while ( have_posts() ) : the_post(); the_content(); endwhile; ?></div></div>
<div class="about-visual reveal-clip" style="margin-top:60px;min-height:460px;background-image:url(<?php echo esc_url( PG_URI . '/assets/hero-space.webp' ); ?>)"></div></div></section>
<section class="section dark"><div class="container"><div class="metrics reveal" style="margin-top:0"><?php foreach ( pg_t( 'home.metrics', array() ) as $m ) : ?><div class="metric"><strong data-count="<?php echo esc_attr( $m['value'] ); ?>" data-suffix="<?php echo esc_attr( $m['suffix'] ); ?>"><?php echo esc_html( $m['value'] . $m['suffix'] ); ?></strong><span><?php echo esc_html( $m['label'] ); ?></span></div><?php endforeach; ?></div></div></section>
<section class="section"><div class="container"><div class="eyebrow orange reveal"><?php echo esc_html( $p['values_eyebrow'] ); ?></div><h2 class="h2" data-split style="margin:14px 0 40px"><?php echo esc_html( $p['values_title'] ); ?></h2>
<div class="values" data-stagger><?php foreach ( $p['values'] as $i => $v ) : ?><div class="value spot reveal" style="position:relative"><span class="num"><?php printf( '%02d', $i + 1 ); ?></span><h3><?php echo esc_html( $v['title'] ); ?></h3><p><?php echo esc_html( $v['text'] ); ?></p></div><?php endforeach; ?></div></div></section>
<section class="section soft"><div class="container"><div class="eyebrow orange reveal"><?php echo esc_html( $p['leadership_eyebrow'] ); ?></div><h2 class="h2" data-split style="margin:14px 0 40px"><?php echo esc_html( $p['leadership_title'] ); ?></h2>
<div class="leaders" data-stagger><?php foreach ( $p['leaders'] as $l ) : ?><div class="leader reveal"><div class="ph"></div><h3><?php echo esc_html( $l['name'] ); ?></h3><div class="role"><?php echo esc_html( $l['role'] ); ?></div><p><?php echo esc_html( $l['bio'] ); ?></p></div><?php endforeach; ?></div></div></section>
<?php get_template_part( 'template-parts/cta' ); get_footer(); ?>
