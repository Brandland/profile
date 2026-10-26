<?php
get_header();
$p = pg_t( 'work_page' );
get_template_part( 'template-parts/page-hero', null, array( 'eyebrow' => $p['eyebrow'], 'title' => $p['title'], 'lead' => $p['lead'] ) );
?>
<section class="section soft"><div class="container">
<div class="filters reveal" role="group"><button class="filter-btn active" data-filter="all" aria-pressed="true"><?php pg_e( 'ui.filter_all' ); ?></button>
<?php foreach ( $p['filters'] as $f ) : ?><button class="filter-btn" data-filter="<?php echo esc_attr( $f['key'] ); ?>" aria-pressed="false"><?php echo esc_html( $f['label'] ); ?></button><?php endforeach; ?></div>
<div class="case-grid" data-stagger aria-live="polite">
<?php
while ( have_posts() ) { the_post(); get_template_part( 'template-parts/case-card' ); }
?>
</div></div></section>
<?php get_template_part( 'template-parts/cta' ); get_footer(); ?>
