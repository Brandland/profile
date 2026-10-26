<?php
get_header();
while ( have_posts() ) : the_post(); $cat = get_the_category(); ?>
<section class="case-hero"><div class="container">
<a class="crumb" href="<?php echo esc_url( pg_url( 'insights' ) ); ?>">← <?php pg_e( 'ui.nav.insights' ); ?></a>
<div class="eyebrow orange reveal"><?php echo esc_html( $cat ? $cat[0]->name . ' · ' : '' ); ?><?php echo (int) pg_reading_time(); ?> <?php pg_e( 'ui.min_read' ); ?> · <?php echo esc_html( get_the_date() ); ?></div>
<h1 class="h1" data-split style="margin-top:16px;max-width:1000px"><?php the_title(); ?></h1>
<?php if ( has_excerpt() ) : ?><p class="lead reveal" style="margin-top:24px"><?php echo esc_html( get_the_excerpt() ); ?></p><?php endif; ?>
</div></section>
<?php if ( has_post_thumbnail() ) : ?><section><div class="container"><div class="case-cover"><div class="case-media" style="background:url(<?php echo esc_url( get_the_post_thumbnail_url( null, 'pg-cover' ) ); ?>) center/cover"></div></div></div></section><?php endif; ?>
<section class="section tight"><div class="container"><div class="article reveal"><?php the_content(); ?><?php get_template_part( 'template-parts/share' ); ?></div></div></section>
<?php endwhile;
$p = pg_t( 'insights_page' );
get_template_part( 'template-parts/linkedin', null, array( 'eyebrow' => $p['newsletter_eyebrow'], 'title' => $p['newsletter_title'], 'lead' => $p['newsletter_lead'] ) );
get_footer();
