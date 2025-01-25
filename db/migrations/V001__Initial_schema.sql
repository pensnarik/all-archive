create schema aa;

create type aa.t_image_type as enum ('jpge', 'png', 'bmp', 'gif');

create sequence file_id_seq start with 100000000 increment by 1;

create table aa.file
(
    id                      bigint primary key default nextval('file_id_seq'),
    path                    text not null,
    md5_hash                char(32) not null,
    size                    bigint not null,
    ctime                   timestamp without timezone
);

create sequence image_id_seq start with 200000000 increment by 1;

create table aa.image
(
    id                      bigint primary key default nextval('aa.image_id_seq'),
    file_id                 bigint not null references aa.file(id),
    width                   smallint not null,
    height                  smallint not null,
    image_type              aa.t_image_type not null,
);

alter table aa.image add constraint image_size_check (width > 0 and height > 0);

create sequence aa.exif_key_id_seq start with 1 increment by 1;

create table aa.exif_key
(
    id                      smallint primary key default nextval('aa.exif_key_id_seq'),
    name                    text not null
);

create sequence exif_id_seq start with 300000000 increment by 1;

create table aa.exif
(
    id                      bigint primary key default nextval('aa.exif_id_seq'),
    image_id                bigint not null references aa.image(id),
    key_id                  smallint not null references aa.exit_key(id),
    value                   text
);