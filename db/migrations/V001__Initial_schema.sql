create schema aa;

create type aa.t_file_type as enum ('unknown', 'image', 'video', 'archive', 'text');
create type aa.t_image_type as enum ('unknown', 'jpeg', 'png', 'bmp', 'gif', 'webp');

create sequence aa.file_id_seq start with 100000000 increment by 1;

create table aa.file
(
    id                      bigint primary key default nextval('aa.file_id_seq'),
    path                    text not null,
    md5_hash                char(32) not null,
    size                    bigint not null,
    ctime                   timestamp without time zone
);

create sequence aa.image_file_id_seq start with 200000000 increment by 1;

create table aa.image_file
(
    id                      bigint primary key default nextval('aa.image_file_id_seq'),
    file_id                 bigint not null references aa.file(id),
    width                   smallint not null,
    height                  smallint not null,
    image_type              aa.t_image_type not null
);

alter table aa.image_file add constraint image_size_check check (width > 0 and height > 0);

create sequence aa.exif_key_id_seq start with 1 increment by 1;

create table aa.exif_key
(
    id                      smallint primary key default nextval('aa.exif_key_id_seq'),
    name                    text not null
);

create sequence aa.exif_id_seq start with 300000000 increment by 1;

create table aa.exif
(
    id                      bigint primary key default nextval('aa.exif_id_seq'),
    image_file_id           bigint not null references aa.image_file(id),
    key_id                  smallint not null references aa.exif_key(id),
    value                   text
);