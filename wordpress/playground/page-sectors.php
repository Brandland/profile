<?php
/* Template Name: Sectors */
get_header();
$p = pg_t( 'sectors_page' );
get_template_part( 'template-parts/page-hero', null, array( 'eyebrow' => $p['eyebrow'], 'title' => $p['title'], 'lead' => $p['lead'] ) );
?>
<section class="section soft"><div class="container"><div class="sector-list" data-stagger>
<?php foreach ( pg_t( 'sectors', array() ) as $i => $s ) : ?><a class="sector reveal" href="<?php echo esc_url( pg_url( 'work' ) . '#' . $s['slug'] ); ?>"><span class="num"><?php printf( '%02d', $i + 1 ); ?></span><span class="name"><?php echo esc_html( $s['name'] ); ?></span><span class="arr">↗</span><span class="sector-text"><?php echo esc_html( $s['text'] ); ?></span></a><?php endforeach; ?>
</div></div></section>
<section class="section"><div class="container"><div class="intro-split"><div class="sticky-title"><div class="eyebrow orange reveal"><?php echo esc_html( $p['intel_eyebrow'] ); ?></div><h2 class="h2" data-split style="margin-top:14px"><?php echo esc_html( $p['intel_title'] ); ?></h2></div>
<div class="reveal"><p class="lead"><?php echo esc_html( $p['intel_lead'] ); ?></p><p class="copy"><?php echo esc_html( $p['intel_copy'] ); ?></p><div class="quote"><p><?php echo esc_html( $p['quote'] ); ?></p><span><?php echo esc_html( $p['quote_by'] ); ?></span></div></div></div></div></section>
<?php get_template_part( 'template-parts/cta' ); get_footer(); ?>
