<?php
/** LinkedIn block. Args: eyebrow, title, lead. */
$a = wp_parse_args( $args ?? array(), array(
	'eyebrow' => pg_t( 'home.linkedin_eyebrow' ),
	'title'   => pg_t( 'home.linkedin_title' ),
	'lead'    => pg_t( 'home.linkedin_lead' ),
) );
$embeds = pg_linkedin_embeds();
?>
<section class="section"><div class="container"><div class="li-panel reveal">
<div><div class="li-mark"><?php echo pg_icon_linkedin(); // phpcs:ignore ?></div><div class="eyebrow orange"><?php echo esc_html( $a['eyebrow'] ); ?></div>
<h2 class="h2" style="margin-top:14px"><?php echo esc_html( $a['title'] ); ?></h2><p class="copy"><?php echo esc_html( $a['lead'] ); ?></p>
<?php if ( pg_option( 'linkedin_url' ) ) : ?><a class="btn linkedin magnetic" href="<?php echo esc_url( pg_option( 'linkedin_url' ) ); ?>" target="_blank" rel="noopener"><?php echo pg_icon_linkedin(); // phpcs:ignore ?> <?php pg_e( 'ui.follow_linkedin' ); ?></a><?php endif; ?></div>
<?php if ( $embeds ) : ?>
<div class="li-embeds"><?php echo implode( '', $embeds ); // phpcs:ignore -- escaped in pg_linkedin_embeds ?></div>
<?php else : ?>
<div class="li-posts" data-stagger>
<?php
$recent = get_posts( array( 'posts_per_page' => 3 ) );
foreach ( $recent as $p ) : ?>
<a class="li-post reveal" href="<?php echo esc_url( get_permalink( $p ) ); ?>"><img src="<?php echo esc_url( PG_URI . '/assets/playground-mark.png' ); ?>" alt=""><div><small>Playground · <?php echo esc_html( get_the_date( '', $p ) ); ?></small><p><?php echo esc_html( get_the_title( $p ) ); ?></p></div></a>
<?php endforeach; ?>
</div>
<?php endif; ?>
</div></div></section>
