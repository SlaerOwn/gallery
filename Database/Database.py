from __future__ import annotations
from functools import reduce
import os
from pathlib import Path
from typing import Any, List

from databases import Database
from Models.Admin import AdminInDatabase
from Models.Images import ImageWithAllInfo, ImageWithAllInfoInDatabase, SectionInDatabase, TagInDatabase
from Utils import *
from Utils.Env import EnvClass

class DatabaseError(Exception): pass
class UserExists(DatabaseError): pass
class UserNotExists(DatabaseError): pass
class PhotoNotExists(DatabaseError): pass
class CommentNotExists(DatabaseError): pass

class DatabaseConnectionError(DatabaseError): pass
class DatabaseTransactionError(DatabaseError): pass

class DatabaseBaseClass:
    def __init__(self):
        self.path_to_database = "database.db"
        self.database_inited: bool = False
        self.Hasher = Hasher.HasherClass()
        self.database: Database | None = None
        self.Env = EnvClass()
        

    async def database_init(self):
        self.database = Database(self.Env.env["GALLERY_DATABASE_URL"])
        await self.database.connect()
        self.database_inited = True
        try:
            await self.request(
                'CREATE TABLE IF NOT EXISTS admin('\
                '    hashOfPassword TEXT PRIMARY KEY,'\
                '    aboutMe TEXT UNIQUE,'\
                '    avatar TEXT);'
            )
            await self.request(
                'CREATE TABLE IF NOT EXISTS images('\
                '    imageId INTEGER PRIMARY KEY AUTOINCREMENT,'\
                '    image TEXT NOT NULL);'
            )
            await self.request(
                'CREATE TABLE IF NOT EXISTS images_to_tags('\
                '    imageId INTEGER,'\
                '    tagId INTEGER, '\
                '    UNIQUE("imageId","tagId"));'
            )
            await self.request(
                'CREATE TABLE IF NOT EXISTS tags('\
                '    tagId INTEGER PRIMARY KEY AUTOINCREMENT,'\
                '    tag TEXT);'
            )
            await self.request(
                'CREATE TABLE IF NOT EXISTS tags_to_sections('\
                '    tagId INTEGER,'\
                '    sectionId INTEGER, '\
                '    UNIQUE("tagId","sectionId"));'
            )
            await self.request(
                'CREATE TABLE IF NOT EXISTS sections('\
                '    sectionId INTEGER PRIMARY KEY AUTOINCREMENT,'\
                '    section TEXT);'
            )
            hashOfPassword = await self.request("SELECT hashOfPassword FROM admin")
            if(hashOfPassword and hashOfPassword[0]["hashOfPassword"]): ...
            else:
                await self.request('INSERT INTO admin(hashOfPassword) VALUES(:hash);', \
                        hash=self.Hasher.PasswordHash(self.Env.env["GALLERY_ADMIN_PASSWORD"]))
        except Exception as e:
            print(e)
            self.database_inited = False
        finally:
            return self.database_inited

    async def database_uninit(self):
        if(self.database): await self.database.disconnect()

    async def request(self, request: str, *args: dict[str, str | int], **other: str | int):
        if(not self.database_inited or self.database == None):
            if(not await self.database_init()):
                raise DatabaseConnectionError()
        try:
            common_dict = {key: value for dict in [*args, other] for key, value in dict.items()}
            if("select" not in request.lower()):
                await self.database.execute(request, common_dict) #type: ignore
                return None
            else:
                response: list[dict[str, Any]] = \
                    list(map(
                        lambda x: dict(x), #type: ignore
                        await self.database.fetch_all(request, common_dict) #type: ignore
                    ))
                return response
        except Exception as e:
            print(f"Request error - {e}")
            raise DatabaseTransactionError()

    def imageFromLineToTree(self, images_from_database: List[ImageWithAllInfoInDatabase]): 
        images: List[ImageWithAllInfo] = []
        if(images_from_database):
            for image in images_from_database:
                if(len(images) != 0 and image["imageId"] == images[-1]["imageId"]):
                    if(image["tagId"]):
                        images[-1]["tags"].append(TagInDatabase(tagId=image["tagId"], tag=image["tag"]))
                    if(image["sectionId"]):
                        images[-1]["sections"].append(
                            SectionInDatabase(sectionId=image["sectionId"], section=image["section"])
                        )
                else: 
                    images.append(
                        ImageWithAllInfo(
                            imageId=image["imageId"], 
                            image=image["image"], 
                            tags=[TagInDatabase(tagId=image["tagId"], tag=image["tag"])] 
                                        if image["tagId"] else [], 
                            sections=[SectionInDatabase(sectionId=image["sectionId"], section=image["section"])] 
                                            if image["sectionId"] else [], 
                        ))
        return images

class DatabaseClass(DatabaseBaseClass):

    # --- REQUESTS ---

    getAdminRequest = "SELECT * FROM admin"
    getPasswordRequest = "SELECT hashOfPassword FROM admin"
    getInfoRequest = "SELECT aboutMe FROM admin"
    editInfoRequest = "UPDATE admin set aboutMe=:aboutMe"
    #addPhotoRequest = "INSERT INTO images(image, tags) VALUES(:image, :tags);"
    createTagRequest = "INSERT INTO tags(tag) VALUES(:tag);"
    deleteTagRequest = "DELETE FROM tags WHERE tagId=:tagId"
    createSectionRequest = "INSERT INTO sections(section, includedTags) VALUES(:section, :includedTags);"
    deleteSectionRequest = "DELETE FROM sections WHERE sectionId=:sectionId"
    #getAllPhotosRequest = "SELECT * FROM images"
    #getSectionPhotosRequest = "SELECT * FROM images WHERE sectionId=:sectionId"
    getSectionsRequest = "SELECT * FROM sections"
    getTagsRequest = "SELECT * FROM tags"

    # - ADMIN INFO -
    # - IMAGES -
    getAllImagesRequest = "SELECT images.*, tags.*, sections.* FROM images "\
                    "LEFT OUTER JOIN images_to_tags itt ON itt.imageId = images.imageId "\
                    "LEFT OUTER JOIN tags ON itt.tagId = tags.tagId "\
                    "LEFT OUTER JOIN tags_to_sections tts ON tts.tagId = tags.tagId "\
                    "LEFT OUTER JOIN sections ON sections.sectionId = tts.sectionId "\
                    "ORDER BY images.imageId"
    getSectionImagesRequest = "SELECT images.*, tags.*, sections.* FROM images "\
                    "LEFT OUTER JOIN images_to_tags itt ON itt.imageId = images.imageId "\
                    "LEFT OUTER JOIN tags ON itt.tagId = tags.tagId "\
                    "LEFT OUTER JOIN tags_to_sections tts ON tts.tagId = tags.tagId "\
                    "LEFT OUTER JOIN sections ON sections.sectionId = tts.sectionId "\
                    "WHERE sections.sectionId = :sectionId ORDER BY images.imageId"
    addImageRequest = "INSERT INTO images(image) VALUES(:image);"
    getLastImageId = "SELECT MAX(imageId) FROM images"

    # - TAGS -
    addTagToImageRequest = "INSERT or IGNORE INTO images_to_tags VALUES(:imageId, :tagId);"

    # - SECTIONS -

    

    # --- FUNCTIONS ---

    # - ADMIN INFO -
    async def get_admin(self) -> AdminInDatabase | None:
        response: List[AdminInDatabase] | None \
                = await self.request(self.getAdminRequest) #type: ignore
        return response[0] if response and len(response)>0 else None

    async def get_password(self) -> str:
        password = await self.request(self.getPasswordRequest)
        return password[0]

    async def get_info(self) -> str:
        info = await self.request(self.getInfoRequest)
        return info[0] 

    async def edit_info(self, info: str) -> None:
        await self.request(self.editInfoRequest, {"aboutMe": info})

    # - TAGS -
    async def add_tag_to_image(self, imageId: int, tagId: int):
        await self.request(self.addTagToImageRequest, imageId=imageId, tagId=tagId)

    async def create_tag(self, tag: str) -> None:
        await self.request(self.createTagRequest, tag=tag)

    async def delete_tag(self, tagId: int) -> None:
        await self.request(self.deleteTagRequest, {"tagId": tagId})

    async def get_tags(self) -> list:
        tags: List[TagInDatabase] | None \
            = await self.request(self.getTagsRequest) #type: ignore
        return tags if tags else []

    # - SECTIONS -
    async def get_sections(self) -> list[SectionInDatabase]:
        sections: List[SectionInDatabase] | None \
            = await self.request(self.getSectionsRequest) #type: ignore
        return sections if sections else []

    async def create_section(self, section: str, includedTagsList) -> None:
        includedTags = ";".join(includedTagsList)
        await self.request(self.createSectionRequest, {"section": section, "includedTags": includedTags})

    async def delete_section(self, sectionId: int) -> None:
        await self.request(self.deleteSectionRequest, {"sectionId": sectionId})

    # - IMAGES -
    async def get_all_images(self) -> List[ImageWithAllInfo]:
        images: List[ImageWithAllInfoInDatabase] | None \
                = await self.request(self.getAllImagesRequest) #type: ignore
        return self.imageFromLineToTree(images) if images else []

    async def get_section_images(self, sectionId: int) -> List[ImageWithAllInfo]:
        images: List[ImageWithAllInfoInDatabase] | None \
                = await self.request(self.getSectionImagesRequest, sectionId=sectionId) #type: ignore
        return self.imageFromLineToTree(images) if images else []

    async def add_image(self, filePath: str) -> int:
        await self.request(self.addImageRequest, image=filePath)
        newImageIdRequestResult = await self.request(self.getLastImageId)
        if(newImageIdRequestResult is None): raise DatabaseError()
        return newImageIdRequestResult[0]["MAX(imageId)"]