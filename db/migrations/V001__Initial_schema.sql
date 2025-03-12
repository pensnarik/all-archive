create schema aa;

create type aa.t_file_type as enum ('unknown', 'image', 'video', 'archive', 'text');
create type aa.t_image_type as enum ('unknown', 'jpeg', 'png', 'bmp', 'gif', 'webp', 'invalid');
create type aa.t_storage_container_type as enum ('archive', 'ext3', 'ext4', 'iso9660', 'ntfs', 'vfat');

create sequence aa.storage_container_id_seq start with 1 increment by 1;

create table aa.storage_container
(
    id                      bigint primary key default nextval('aa.storage_container_id_seq'),
    container_type          aa.t_storage_container_type not null,
    name                    text not null,
    label                   text,
    fs_uuid                 text
);

create unique index storage_container_fs_uuid_idx on aa.storage_container(fs_uuid);

create sequence aa.file_id_seq start with 100000000 increment by 1;

create table aa.file
(
    id                      bigint primary key default nextval('aa.file_id_seq'),
    container_id            bigint not null references aa.storage_container(id),
    path                    text not null,
    md5_hash                char(32) not null,
    size                    bigint not null,
    ctime                   timestamp without time zone
);

create unique index file_path_idx on aa.file (container_id, path);
create index file_md5_hash_idx on aa.file (md5_hash);

create sequence aa.image_file_id_seq start with 200000000 increment by 1;

create table aa.image_file
(
    id                      bigint primary key,
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

create sequence aa.video_id_seq start with 400000000 increment by 1;

create table aa.video
(
    id                      bigint primary key default nextval('aa.video_id_seq'),
    file_id                 bigint not null references aa.file(id),
    width                   smallint not null,
    height                  smallint not null,
    duration                numeric(8, 2)
);
