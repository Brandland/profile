</main>
<footer class="footer"><div class="container"><div class="footer-grid">
<div class="footer-logo"><img src="<?php echo esc_url( PG_URI . '/assets/playground-logo.png' ); ?>" alt="Playground" width="170" height="49"><p style="max-width:310px;margin-top:18px"><?php pg_e( 'ui.footer_tagline' ); ?></p></div>
<div><h4><?php pg_e( 'ui.footer_navigate' ); ?></h4>
<?php foreach ( array( 'expertise', 'sectors', 'work', 'about' ) as $k ) : ?><a href="<?php echo esc_url( pg_url( $k ) ); ?>"><?php pg_e( 'ui.nav.' . $k ); ?></a><?php endforeach; ?>
</div>
<div><h4><?php pg_e( 'ui.footer_connect' ); ?></h4>
<a href="<?php echo esc_url( pg_url( 'contact' ) ); ?>"><?php pg_e( 'ui.nav.contact' ); ?></a>
<a href="<?php echo esc_url( pg_url( 'insights' ) ); ?>"><?php pg_e( 'ui.nav.insights' ); ?></a>
<?php if ( pg_option( 'linkedin_url' ) ) : ?><a class="social" href="<?php echo esc_url( pg_option( 'linkedin_url' ) ); ?>" target="_blank" rel="noopener"><?php echo pg_icon_linkedin(); // phpcs:ignore ?> LinkedIn</a><?php endif; ?>
</div>
<div><h4><?php pg_e( 'ui.footer_based' ); ?></h4><?php foreach ( pg_t( 'ui.footer_based_lines', array() ) as $line ) { echo '<p>' . esc_html( $line ) . '</p>'; } ?></div>
</div>
<div class="footer-bottom"><span><?php pg_e( 'ui.footer_rights' ); ?><?php $pp = get_privacy_policy_url(); if ( $pp ) : ?> · <a href="<?php echo esc_url( $pp ); ?>" style="display:inline"><?php pg_e( 'ui.footer_privacy' ); ?></a><?php endif; ?></span><span><?php pg_e( 'ui.footer_motto' ); ?></span></div>
</div></footer>
<?php if ( pg_option( 'linkedin_partner_id' ) ) : ?>
<div class="cookie" role="dialog" aria-live="polite" aria-label="Cookies"><p><?php pg_e( 'cookie.text' ); ?></p><button type="button"><?php pg_e( 'cookie.decline' ); ?></button><button type="button" class="ok"><?php pg_e( 'cookie.accept' ); ?></button></div>
<?php endif; ?>
<?php wp_footer(); ?>
</body>
</html>
