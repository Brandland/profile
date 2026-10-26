<?php
/** Page hero. Args: eyebrow, title, lead, extra (html). */
$a = wp_parse_args( $args ?? array(), array( 'eyebrow' => '', 'title' => '', 'lead' => '', 'extra' => '' ) );
?>
<section class="page-hero"><div class="container">
<?php if ( $a['eyebrow'] ) : ?><div class="eyebrow orange reveal"><?php echo esc_html( $a['eyebrow'] ); ?></div><?php endif; ?>
<h1 class="h1" data-split><?php echo esc_html( $a['title'] ); ?></h1>
<?php if ( $a['lead'] ) : ?><p class="lead reveal"><?php echo esc_html( $a['lead'] ); ?></p><?php endif; ?>
<?php echo $a['extra']; // phpcs:ignore -- built from escaped values ?>
</div></section>
