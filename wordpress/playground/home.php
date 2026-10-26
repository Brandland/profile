<?php
/** Insights (blog posts index). */
get_header();
$p = pg_t( 'insights_page' );
get_template_part( 'template-parts/page-hero', null, array( 'eyebrow' => $p['eyebrow'], 'title' => $p['title'], 'lead' => $p['lead'] ) );
?>
<section class="section soft"><div class="container">
<?php if ( have_posts() ) : ?><div class="case-grid" data-stagger>
<?php while ( have_posts() ) : the_post(); $cat = get_the_category(); ?>
<a class="case-card reveal" href="<?php the_permalink(); ?>"><div class="case-media <?php echo has_post_thumbnail() ? '' : 'space'; ?>"<?php echo has_post_thumbnail() ? ' style="background:url(' . esc_url( get_the_post_thumbnail_url( null, 'pg-card' ) ) . ') center/cover"' : ''; ?>></div>
<div class="case-body"><div class="tag"><?php echo esc_html( $cat ? $cat[0]->name : '' ); ?> · <?php echo (int) pg_reading_time(); ?> <?php pg_e( 'ui.min_read' ); ?></div><h3><?php the_title(); ?></h3><p><?php echo esc_html( get_the_excerpt() ); ?></p></div></a>
<?php endwhile; ?></div>
<div class="filters" style="margin-top:30px"><?php echo paginate_links( array( 'type' => 'plain' ) ); // phpcs:ignore ?></div>
<?php endif; ?>
</div></section>
<?php get_template_part( 'template-parts/linkedin', null, array( 'eyebrow' => $p['newsletter_eyebrow'], 'title' => $p['newsletter_title'], 'lead' => $p['newsletter_lead'] ) ); ?>
<?php get_footer(); ?>
