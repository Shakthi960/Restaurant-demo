-- =============================================================================
--   GALAXY RESTAURANTS — seed data
--   Run AFTER schema.sql. Re-runnable: any previous seed rows are removed
--   first, then re-inserted. Live reservations and contact messages are
--   never touched.
-- =============================================================================

-- Remove previously seeded rows (identified by seed-owned keys) before
-- inserting fresh copies below.
delete from public.dishes where name in (
    'Galaxy Dum Biryani', 'Chettinad Chicken Curd Rice', 'Palak Paneer Naan Roll',
    'Golden Ghee Masala Dosa', 'Kashmiri Rogan Josh', 'Saffron Gulab Jamun',
    'Paneer Tikka', 'Chicken 65', 'Samosa Chaat',
    'Butter Chicken', 'Paneer Butter Masala', 'Dal Makhani', 'Meen Moilee',
    'Garlic Butter Naan', 'Tandoori Roti', 'Jeera Pulao',
    'Rasmalai', 'Kesar Kulfi'
);

delete from public.gallery_images where image in (
    'assets/images/gallery/interior-1.jpg', 'assets/images/gallery/chef.jpg',
    'assets/images/gallery/spices.jpg', 'assets/images/gallery/interior-2.jpg',
    'assets/images/gallery/ambiance.jpg', 'assets/images/gallery/detail.jpg'
);

delete from public.reviews where author in ('Meera Krishnan', 'Arjun Mehta', 'Priya Nair');

-- -----------------------------------------------------------------------------
-- Menu
-- -----------------------------------------------------------------------------
insert into public.dishes (name, description, price, region, category, image, is_signature, sort_order) values
-- Signature dishes (6)
('Galaxy Dum Biryani', 'Fragrant basmati layered with saffron, slow-cooked with spiced mutton under a sealed dum.', 385.00, 'South Indian', 'signature', 'assets/images/dishes/biryani.jpg', true, 1),
('Chettinad Chicken Curd Rice', 'Fiery Chettinad-style chicken with cucumber ribbons and tempered cumin curd rice.', 345.00, 'South Indian', 'signature', 'assets/images/dishes/chettinad.jpg', true, 2),
('Palak Paneer Naan Roll', 'Village-style paneer in silky spinach gravy, folded into a blistered tandoori naan.', 295.00, 'North Indian', 'signature', 'assets/images/dishes/paneer-naan.jpg', true, 3),
('Golden Ghee Masala Dosa', 'Crisp golden dosa, potato masala and a drizzle of smoked ghee with three chutneys.', 175.00, 'South Indian', 'signature', 'assets/images/dishes/dosa.jpg', true, 4),
('Kashmiri Rogan Josh', 'Slow-braised lamb in a velvet Kashmiri gravy of browned onions, yogurt and warm spices.', 425.00, 'North Indian', 'signature', 'assets/images/dishes/rogan-josh.jpg', true, 5),
('Saffron Gulab Jamun', 'Warm dumplings soaked in saffron-cardamom syrup, served with pistachio crumble.', 165.00, 'North Indian', 'signature', 'assets/images/dishes/gulab-jamun.jpg', true, 6);

-- -----------------------------------------------------------------------------
-- Full menu (additional items for the /menu page)
-- -----------------------------------------------------------------------------
insert into public.dishes (name, description, price, region, category, image, is_signature, sort_order) values
('Paneer Tikka', 'Char-grilled cottage cheese with mint chutney and pickled onions.', 265.00, 'North Indian', 'starters', 'assets/images/dishes/biryani.jpg', false, 1),
('Chicken 65', 'Fiery South Indian fried chicken tossed with curry leaves and green chilli.', 285.00, 'South Indian', 'starters', 'assets/images/dishes/chettinad.jpg', false, 2),
('Samosa Chaat', 'Savoury samosas under spiced chickpeas, yogurt and tamarind drizzle.', 195.00, 'North Indian', 'starters', 'assets/images/dishes/paneer-naan.jpg', false, 3);

insert into public.dishes (name, description, price, region, category, image, is_signature, sort_order) values
('Butter Chicken', 'Tandoori chicken simmered in a silky tomato-butter gravy with fenugreek.', 355.00, 'North Indian', 'mains', 'assets/images/dishes/rogan-josh.jpg', false, 1),
('Paneer Butter Masala', 'Cottage cheese in a slow-cooked makhani gravy, house technique.', 315.00, 'North Indian', 'mains', 'assets/images/dishes/paneer-naan.jpg', false, 2),
('Dal Makhani', 'Black urad dal and red kidney beans cooked overnight with butter and cream.', 245.00, 'North Indian', 'mains', 'assets/images/dishes/biryani.jpg', false, 3),
('Meen Moilee', 'Kerala-style fish simmered in coconut milk with curry leaves and green chilli.', 325.00, 'South Indian', 'mains', 'assets/images/dishes/chettinad.jpg', false, 4);

insert into public.dishes (name, description, price, region, category, image, is_signature, sort_order) values
('Garlic Butter Naan', 'Tandoor-baked flatbread brushed with garlic butter.', 90.00, 'North Indian', 'breads', 'assets/images/dishes/paneer-naan.jpg', false, 1),
('Tandoori Roti', 'Whole-wheat roti baked in the clay oven.', 55.00, 'North Indian', 'breads', 'assets/images/dishes/dosa.jpg', false, 2),
('Jeera Pulao', 'Basmati rice tempered with cumin and whole spices.', 175.00, 'North Indian', 'breads', 'assets/images/dishes/biryani.jpg', false, 3);

insert into public.dishes (name, description, price, region, category, image, is_signature, sort_order) values
('Rasmalai', 'Cottage cheese discs soaked in saffron milk with pistachio slivers.', 145.00, 'North Indian', 'desserts', 'assets/images/dishes/gulab-jamun.jpg', false, 1),
('Kesar Kulfi', 'Saffron and cardamom Kulfi served with rose falooda.', 135.00, 'North Indian', 'desserts', 'assets/images/dishes/dosa.jpg', false, 2);

-- -----------------------------------------------------------------------------
-- Locations
-- -----------------------------------------------------------------------------
insert into public.locations (slug, city, address, hours, phone, lat, lng, sort_order) values
('chennai',   'Chennai',    'No. 24, Cathedral Road, Gopalapuram,<br>Chennai, Tamil Nadu 600 086',       'Open Daily · 11:30 AM – 11:00 PM', '+91 44 2811 0001', 13.0418, 80.2686, 1),
('bengaluru', 'Bengaluru',  '4th Floor, Vittal Mallya Road,<br>Karnataka 560 001',                      'Open Daily · 11:30 AM – 11:00 PM', '+91 80 2222 0002', 12.9716, 77.5946, 2),
('hyderabad', 'Hyderabad',  'Road No. 1, Banjara Hills,<br>Hyderabad, Telangana 500 034',               'Open Daily · 12:00 PM – 12:00 AM', '+91 40 2355 0003', 17.4156, 78.4340, 3),
('mumbai',    'Mumbai',     'Juhu Tara Road, Juhu,<br>Mumbai, Maharashtra 400 049',                     'Open Daily · 11:30 AM – 12:30 AM', '+91 22 2660 0004', 19.1075, 72.8262, 4),
('delhi',     'Delhi',      'Connaught Place, Block A,<br>New Delhi 110 001',                           'Open Daily · 12:00 PM – 11:00 PM', '+91 11 2341 0005', 28.6315, 77.2167, 5),
('kolkata',   'Kolkata',    'Park Street Area, Free School Street,<br>Kolkata, West Bengal 700 016',    'Open Daily · 12:00 PM – 11:00 PM', '+91 33 2265 0006', 22.5558, 88.3581, 6)
on conflict (slug) do nothing;

-- -----------------------------------------------------------------------------
-- Gallery
-- -----------------------------------------------------------------------------
insert into public.gallery_images (caption, alt, image, span_class, sort_order) values
('The Grand Dining Hall',     'Galaxy Restaurants grand dining hall with warm lighting',          'assets/images/gallery/interior-1.jpg', 'gallery-item--tall', 1),
('The Craft of Plating',      'Galaxy chef plating a traditional dish with precision',           'assets/images/gallery/chef.jpg',        'gallery-item--wide', 2),
('Colours of the Spice Shelf','Aromatic Indian spices in brass bowls',                            'assets/images/gallery/spices.jpg',      '',                   3),
('Intimate Alcoves',          'Private dining alcove with brass lamps and jali screens',          'assets/images/gallery/interior-2.jpg', 'gallery-item--wide', 4),
('Evenings at Galaxy',        'Evening ambiance with soft lamplight across the restaurant',       'assets/images/gallery/ambiance.jpg',    '',                   5),
('Details in Brass & Wood',   'Traditional brass lamp and carved decorative detail',               'assets/images/gallery/detail.jpg',      '',                   6);

-- -----------------------------------------------------------------------------
-- Reviews
-- -----------------------------------------------------------------------------
insert into public.reviews (author, city, rating, review) values
('Meera Krishnan', 'Chennai', 5, 'The Dum Biryani took me straight back to my grandmother''s kitchen. Service was thoughtful, and the ambiance is pure old-world charm.'),
('Arjun Mehta',    'Delhi',   5, 'Celebrated our anniversary here. The rogan josh was spectacular and the staff made the whole evening feel special and unhurried.'),
('Priya Nair',     'Bengaluru', 4, 'Beautiful interiors and genuinely traditional flavours. The ghee masala dosa is the star — crisp, generous and deeply comforting.');