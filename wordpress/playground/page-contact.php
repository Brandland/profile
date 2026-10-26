<?php
/* Template Name: Contact */
get_header();
$p = pg_t( 'contact_page' );
$f = $p['form'];
get_template_part( 'template-parts/page-hero', null, array( 'eyebrow' => $p['eyebrow'], 'title' => $p['title'], 'lead' => $p['lead'] ) );
$sent = isset( $_GET['sent'] ) ? sanitize_key( wp_unslash( $_GET['sent'] ) ) : ''; // phpcs:ignore WordPress.Security.NonceVerification
?>
<section class="section"><div class="container"><div class="contact-grid">
<div class="contact-card reveal"><img src="<?php echo esc_url( PG_URI . '/assets/playground-logo-white.png' ); ?>" alt="Playground" style="width:170px"><p style="margin-top:22px"><?php echo esc_html( $p['card_text'] ); ?></p><div class="contact-lines">
<?php foreach ( $p['lines'] as $ln ) :
	$href = 'LINKEDIN' === $ln['href'] ? pg_option( 'linkedin_url' ) : $ln['href']; ?>
<div><small><?php echo esc_html( $ln['label'] ); ?></small><?php if ( $href ) : ?><a href="<?php echo esc_url( $href ); ?>"<?php echo 0 === strpos( $href, 'http' ) ? ' target="_blank" rel="noopener"' : ''; ?>><?php echo esc_html( $ln['value'] ); ?></a><?php else : ?><span style="font-size:18px"><?php echo esc_html( $ln['value'] ); ?></span><?php endif; ?></div>
<?php endforeach; ?></div></div>
<form id="contact-form" class="form reveal" method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
<input type="hidden" name="action" value="pg_contact"><input type="hidden" name="lang" value="<?php echo esc_attr( pg_lang() ); ?>">
<?php wp_nonce_field( 'pg_contact', 'pg_contact_nonce' ); ?>
<?php if ( '1' === $sent ) : ?><p class="field full form-status"><?php echo esc_html( $f['thanks'] ); ?></p><?php elseif ( 'error' === $sent ) : ?><p class="field full form-status" style="color:#b3261e">Please check the required fields.</p><?php endif; ?>
<div class="field"><label for="f-name"><?php echo esc_html( $f['name'] ); ?></label><input id="f-name" name="name" autocomplete="name" required></div>
<div class="field"><label for="f-company"><?php echo esc_html( $f['company'] ); ?></label><input id="f-company" name="company" autocomplete="organization"></div>
<div class="field"><label for="f-email"><?php echo esc_html( $f['email'] ); ?></label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
<div class="field"><label for="f-phone"><?php echo esc_html( $f['phone'] ); ?></label><input id="f-phone" name="phone" type="tel" autocomplete="tel"></div>
<div class="field full"><label for="f-interest"><?php echo esc_html( $f['interest'] ); ?></label><select id="f-interest" name="interest"><?php foreach ( $f['interest_options'] as $o ) { echo '<option>' . esc_html( $o ) . '</option>'; } ?></select></div>
<div class="field full"><label for="f-message"><?php echo esc_html( $f['message'] ); ?></label><textarea id="f-message" name="message" required></textarea></div>
<div class="field full checkbox"><input id="f-consent" name="consent" type="checkbox" value="1" required><label for="f-consent"><?php echo esc_html( $f['consent'] ); ?></label></div>
<div class="hp" aria-hidden="true"><input name="website" tabindex="-1" autocomplete="off"></div>
<div class="field full"><button class="btn primary magnetic" type="submit"><?php echo esc_html( $f['submit'] ); ?> <span class="arrow">↗</span></button><p class="form-note"><?php echo esc_html( $f['note'] ); ?></p></div>
</form></div></div></section>
<?php get_footer(); ?>
